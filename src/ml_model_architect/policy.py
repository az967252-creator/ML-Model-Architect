#!/usr/bin/env python3
"""
run_policy.py - Deterministic Execution Engine and Run Policy Runner.
Enforces that AI agent adheres to the locked plan without deviation, skipping, or tampering.
"""

import sys
import os
import re
import ast
import json
import math
from typing import List, Tuple, Dict, Any

try:
    import jsonschema
except ImportError:
    jsonschema = None

from .locker import verify_plan, validate_plan_schema
from .scanner import SandboxVisitor, Scanner, scan_file, scan_directory
from .enforcer import enforce as enforce_ledger, parse_tables, REQUIRED_HEADERS


KNOWN_TRANSFORMERS = {
    # Preprocessing
    "StandardScaler", "MinMaxScaler", "RobustScaler", "MaxAbsScaler",
    "Normalizer", "Binarizer", "QuantileTransformer", "PowerTransformer",
    "OneHotEncoder", "OrdinalEncoder", "TargetEncoder", "PolynomialFeatures",
    "SplineTransformer", "FunctionTransformer", "KBinsDiscretizer",
    # Impute
    "SimpleImputer", "KNNImputer", "IterativeImputer", "MissingIndicator",
    # Feature Selection
    "SelectKBest", "SelectPercentile", "SelectFpr", "SelectFdr", "SelectFwe",
    "GenericUnivariateSelect", "RFE", "RFECV", "SelectFromModel",
    "SequentialFeatureSelector", "VarianceThreshold",
    # Decomposition
    "PCA", "IncrementalPCA", "KernelPCA", "MiniBatchSparsePCA", "SparsePCA",
    "TruncatedSVD", "FastICA", "FactorAnalysis", "NMF",
    # Composition
    "ColumnTransformer"
}

SPLIT_IDENTIFIERS = {
    "train_test_split", "cross_val_score", "cross_validate",
    "KFold", "StratifiedKFold", "GroupKFold", "TimeSeriesSplit",
    "ShuffleSplit", "StratifiedShuffleSplit", "PredefinedSplit"
}


def _has_stat_call(node: ast.AST) -> bool:
    """Returns True if the AST subtree contains a statistic computation (.mean, .median, .std, etc.)."""
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute):
            if sub.func.attr in {"mean", "median", "std", "var", "mode", "min", "max"}:
                return True
    return False


def _is_groupby_receiver(node: ast.AST) -> bool:
    """Returns True if the AST subtree is a groupby(...) receiver."""
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute) and sub.func.attr == "groupby":
            return True
    return False


class PipelineASTValidator(ast.NodeVisitor):
    def __init__(self):
        self.pipeline_names = set()
        self.pipeline_assignments_count = 0
        self.pipeline_instantiations_count = 0
        self.pipeline_used_in_fit_or_cv = False
        self.train_test_split_lineno = None
        self.leakage_violations = []
        self.imported_pipeline_classes = set()
        self.imported_transformers = {}  # alias -> class_name
        self.transformer_vars = set()  # names of variables holding transformer instances
        self.transformer_containers = set()  # names of containers (lists, dicts, tuples) holding transformers
        self.fitted_before_split_vars = set()
        self.local_functions = {}  # name -> FunctionDef
        self.visiting_functions = set()
        self._inside_column_transformer = False
        self.current_call_context_lineno = None

    def _collect_pass1(self, tree: ast.AST):
        """Pass 1: Discover imports, local functions, and split line numbers across the AST."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                if "sklearn" in mod:
                    for alias in node.names:
                        name = alias.name
                        local_name = alias.asname or name
                        if name in {"Pipeline", "make_pipeline"}:
                            self.imported_pipeline_classes.add(local_name)
                        if name in KNOWN_TRANSFORMERS or any(
                            sub in mod for sub in ["preprocessing", "impute", "feature_selection", "decomposition"]
                        ):
                            self.imported_transformers[local_name] = name
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.name
                    local_name = alias.asname or name
                    if any(sub in name for sub in ["preprocessing", "impute", "feature_selection", "decomposition"]):
                        self.imported_transformers[local_name] = name
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.local_functions[node.name] = node
            elif isinstance(node, ast.Call):
                func = node.func
                func_name = None
                if isinstance(func, ast.Name):
                    func_name = func.id
                elif isinstance(func, ast.Attribute):
                    func_name = func.attr
                if func_name in SPLIT_IDENTIFIERS:
                    if self.train_test_split_lineno is None or node.lineno < self.train_test_split_lineno:
                        self.train_test_split_lineno = node.lineno

    def is_transformer_class(self, name: str) -> bool:
        if name in KNOWN_TRANSFORMERS or name in self.imported_transformers:
            return True
        if any(tok in name.lower() for tok in ["scaler", "imputer", "encoder", "transformer", "pca", "selectkbest"]):
            return True
        return False

    def is_transformer_call(self, call_node: ast.Call) -> bool:
        func = call_node.func
        if isinstance(func, ast.Name):
            return self.is_transformer_class(func.id)
        elif isinstance(func, ast.Attribute):
            if self.is_transformer_class(func.attr):
                return True
            if isinstance(func.value, ast.Name) and func.value.id in self.imported_transformers:
                return True
        return False

    def visit(self, node):
        if not hasattr(self, "_pass1_done"):
            self._pass1_done = True
            self._collect_pass1(node)
        super().visit(node)

    def visit_Assign(self, node):
        effective_lineno = self.current_call_context_lineno or node.lineno

        # Check if right-hand side is Pipeline(...) or make_pipeline(...)
        is_pipe_call = False
        if isinstance(node.value, ast.Call):
            func = node.value.func
            func_name = None
            if isinstance(func, ast.Name):
                func_name = func.id
            elif isinstance(func, ast.Attribute):
                func_name = func.attr
            if func_name in {"Pipeline", "make_pipeline"} or func_name in self.imported_pipeline_classes:
                is_pipe_call = True

        if is_pipe_call:
            self.pipeline_assignments_count += 1
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.pipeline_names.add(target.id)

        # Check if right-hand side is a transformer instance
        is_trans_inst = False
        if isinstance(node.value, ast.Call):
            if self.is_transformer_call(node.value):
                is_trans_inst = True

        if is_trans_inst:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.transformer_vars.add(target.id)

        # Check tuple/list unpacking e.g. scaler, imputer = StandardScaler(), SimpleImputer()
        for target in node.targets:
            if isinstance(target, (ast.Tuple, ast.List)) and isinstance(node.value, (ast.Tuple, ast.List)):
                for elt_target, elt_val in zip(target.elts, node.value.elts):
                    if isinstance(elt_target, ast.Name):
                        if (isinstance(elt_val, ast.Call) and self.is_transformer_call(elt_val)) or (isinstance(elt_val, ast.Name) and elt_val.id in self.transformer_vars):
                            self.transformer_vars.add(elt_target.id)

        # Check list/tuple containers e.g. transformers = [StandardScaler()]
        if isinstance(node.value, (ast.List, ast.Tuple)):
            has_transformer = any(
                (isinstance(elt, ast.Call) and self.is_transformer_call(elt))
                or (isinstance(elt, ast.Name) and elt.id in self.transformer_vars)
                for elt in node.value.elts
            )
            if has_transformer:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.transformer_containers.add(target.id)

        # Check dict containers e.g. t_dict = {"scaler": StandardScaler()}
        if isinstance(node.value, ast.Dict):
            has_transformer = any(
                (isinstance(val, ast.Call) and self.is_transformer_call(val))
                or (isinstance(val, ast.Name) and val.id in self.transformer_vars)
                for val in node.value.values
            )
            if has_transformer:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.transformer_containers.add(target.id)

        # Check variable aliasing (e.g., s2 = s1)
        if isinstance(node.value, ast.Name):
            if node.value.id in self.transformer_vars:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.transformer_vars.add(target.id)
            elif node.value.id in self.transformer_containers:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.transformer_containers.add(target.id)

        # Check pre-split pandas manual scaling via .mean() or .std()
        if (self.train_test_split_lineno is None or effective_lineno < self.train_test_split_lineno) and not self._inside_column_transformer:
            if isinstance(node.value, ast.BinOp):
                if _has_stat_call(node.value.right) or _has_stat_call(node.value.left):
                    self.leakage_violations.append(
                        f"Data leakage detected: pandas pre-split manual mean/std scaling leakage at line {effective_lineno}."
                    )

        self.generic_visit(node)

    def _check_helper_leakage(self, func_name: str, call_lineno: int):
        """Inspects helper function body strictly for pre-split data leakage patterns."""
        if func_name in self.visiting_functions or func_name not in self.local_functions:
            return
        self.visiting_functions.add(func_name)
        try:
            func_node = self.local_functions[func_name]
            # Track local transformer variable assignments within helper
            local_trans_vars = set()
            for node in ast.walk(func_node):
                if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
                    if self.is_transformer_call(node.value):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                local_trans_vars.add(target.id)

            for node in ast.walk(func_node):
                if isinstance(node, ast.Call):
                    fn = node.func
                    fn_name = fn.id if isinstance(fn, ast.Name) else (fn.attr if isinstance(fn, ast.Attribute) else None)
                    c_name = fn.value.id if isinstance(fn, ast.Attribute) and isinstance(fn.value, ast.Name) else ""
                    is_inline = isinstance(fn, ast.Attribute) and isinstance(fn.value, ast.Call) and self.is_transformer_call(fn.value)

                    # Nested helper call
                    if fn_name in self.local_functions:
                        self._check_helper_leakage(fn_name, call_lineno)

                    if fn_name in {"fit", "fit_transform"}:
                        if is_inline:
                            self.leakage_violations.append(
                                f"Data leakage detected in helper function '{func_name}()' (called at line {call_lineno}): inline transformer call '.{fn_name}()' before train_test_split."
                            )
                        elif (
                            c_name in local_trans_vars
                            or self.is_transformer_class(c_name)
                            or any(t in c_name.lower() for t in ["scaler", "encoder", "imputer", "transformer", "pca", "selectkbest"])
                        ):
                            self.leakage_violations.append(
                                f"Data leakage detected in helper function '{func_name}()' (called at line {call_lineno}): '{c_name}.{fn_name}()' called before train_test_split."
                            )
                    elif fn_name == "fillna" and any(_has_stat_call(arg) for arg in node.args):
                        self.leakage_violations.append(
                            f"Data leakage detected in helper function '{func_name}()' (called at line {call_lineno}): pandas fillna(mean/median) called before train_test_split."
                        )
                    elif fn_name == "transform" and isinstance(fn, ast.Attribute) and _is_groupby_receiver(fn.value):
                        self.leakage_violations.append(
                            f"Data leakage detected in helper function '{func_name}()' (called at line {call_lineno}): groupby.transform target encoding called before train_test_split."
                        )
        finally:
            self.visiting_functions.remove(func_name)

    def visit_For(self, node):
        if isinstance(node.iter, ast.Name) and node.iter.id in self.transformer_containers:
            if isinstance(node.target, ast.Name):
                self.transformer_vars.add(node.target.id)
        self.generic_visit(node)

    def visit_Call(self, node):
        effective_lineno = self.current_call_context_lineno or node.lineno
        func = node.func
        func_name = None
        caller_name = ""
        is_inline_transformer = False
        is_subscript_transformer = False

        if isinstance(func, ast.Name):
            func_name = func.id
        elif isinstance(func, ast.Attribute):
            func_name = func.attr
            if isinstance(func.value, ast.Name):
                caller_name = func.value.id
            elif isinstance(func.value, ast.Call):
                if self.is_transformer_call(func.value):
                    is_inline_transformer = True
            elif isinstance(func.value, ast.Subscript):
                sub = func.value
                if isinstance(sub.value, ast.Name) and sub.value.id in self.transformer_containers:
                    is_subscript_transformer = True
                elif isinstance(sub.value, (ast.List, ast.Tuple)):
                    if any((isinstance(e, ast.Call) and self.is_transformer_call(e)) or (isinstance(e, ast.Name) and e.id in self.transformer_vars) for e in sub.value.elts):
                        is_subscript_transformer = True
                elif isinstance(sub.value, ast.Dict):
                    if any((isinstance(v, ast.Call) and self.is_transformer_call(v)) or (isinstance(v, ast.Name) and v.id in self.transformer_vars) for v in sub.value.values):
                        is_subscript_transformer = True

        # Pre-split check flag
        is_pre_split = (self.train_test_split_lineno is None or effective_lineno < self.train_test_split_lineno) and not self._inside_column_transformer

        # Follow calls into locally defined helper functions for data leakage check
        if func_name in self.local_functions and is_pre_split:
            self._check_helper_leakage(func_name, effective_lineno)

        # Check ColumnTransformer boundary
        if func_name in {"ColumnTransformer", "make_column_transformer"}:
            old_inside = self._inside_column_transformer
            self._inside_column_transformer = True
            self.generic_visit(node)
            self._inside_column_transformer = old_inside
            return

        # Direct pipeline instantiation not assigned
        if (func_name in {"Pipeline", "make_pipeline"} or func_name in self.imported_pipeline_classes) and not self._inside_column_transformer:
            self.pipeline_instantiations_count += 1

        # Check cross_val_score / cross_validate usage
        if func_name in {"cross_val_score", "cross_validate"}:
            for arg in node.args:
                if isinstance(arg, ast.Name) and (arg.id in self.pipeline_names or "pipe" in arg.id.lower()):
                    self.pipeline_used_in_fit_or_cv = True
                elif isinstance(arg, ast.Call):
                    subfunc = arg.func
                    sub_name = subfunc.id if isinstance(subfunc, ast.Name) else (subfunc.attr if isinstance(subfunc, ast.Attribute) else None)
                    if sub_name in {"Pipeline", "make_pipeline"} or sub_name in self.imported_pipeline_classes:
                        self.pipeline_used_in_fit_or_cv = True

        # Check Pipeline usage in fit
        if func_name in {"fit", "fit_transform"} and (caller_name in self.pipeline_names or "pipe" in caller_name.lower()):
            self.pipeline_used_in_fit_or_cv = True

        # Pre-split check flag
        is_pre_split = (self.train_test_split_lineno is None or effective_lineno < self.train_test_split_lineno) and not self._inside_column_transformer

        # Check 1: Transformer fit / fit_transform before split
        if func_name in {"fit", "fit_transform"}:
            caller_is_transformer = (
                caller_name in self.transformer_vars
                or caller_name in KNOWN_TRANSFORMERS
                or caller_name in self.imported_transformers
                or any(t in caller_name.lower() for t in ["scaler", "encoder", "imputer", "transformer", "pca", "selectkbest"])
            )
            if is_inline_transformer:
                if is_pre_split:
                    self.leakage_violations.append(
                        f"Data leakage detected: inline transformer call '.{func_name}()' at line {effective_lineno} before train_test_split."
                    )
            elif is_subscript_transformer:
                if is_pre_split:
                    self.leakage_violations.append(
                        f"Data leakage detected: container/subscript transformer '.{func_name}()' called at line {effective_lineno} before train_test_split."
                    )
            elif caller_is_transformer and (caller_name not in self.pipeline_names and "pipe" not in caller_name.lower()):
                if is_pre_split:
                    self.leakage_violations.append(
                        f"Data leakage detected: '{caller_name}.{func_name}()' called at line {effective_lineno} before train_test_split."
                    )
                    self.fitted_before_split_vars.add(caller_name)

        # Check 2: .transform() on transformer fitted before split or calling transform before split
        if func_name == "transform":
            caller_is_transformer = (
                caller_name in self.transformer_vars
                or caller_name in KNOWN_TRANSFORMERS
                or caller_name in self.imported_transformers
                or caller_name in self.fitted_before_split_vars
            )
            if caller_is_transformer and is_pre_split and (caller_name not in self.pipeline_names and "pipe" not in caller_name.lower()):
                self.leakage_violations.append(
                    f"Data leakage detected: '{caller_name}.transform()' called at line {effective_lineno} on pre-split data before train_test_split."
                )

        # Check 3: Pandas fillna(mean/median/std/mode)
        if func_name == "fillna" and is_pre_split:
            if any(_has_stat_call(arg) for arg in node.args):
                self.leakage_violations.append(
                    f"Data leakage detected: pandas pre-split fillna(mean/median) statistic leakage at line {effective_lineno}."
                )

        # Check 4: Pandas groupby().transform(...) target encoding
        if func_name == "transform" and is_pre_split:
            if isinstance(func, ast.Attribute) and _is_groupby_receiver(func.value):
                self.leakage_violations.append(
                    f"Data leakage detected: pandas pre-split groupby-transform target encoding leakage at line {effective_lineno}."
                )

        self.generic_visit(node)


class PolicyEngine:
    def __init__(self, plan_path: str, base_dir: str = None):
        self.plan_path = os.path.abspath(plan_path)
        if base_dir is None:
            self.base_dir = os.path.dirname(self.plan_path)
        else:
            self.base_dir = os.path.abspath(base_dir)
        self.data = validate_plan_schema(self.plan_path)

    def verify_integrity(self) -> bool:
        """Verifies that plan is not tampered with."""
        return verify_plan(self.plan_path)

    def resolve_path(self, rel_path: str) -> str:
        """Resolves path relative to base directory."""
        if os.path.isabs(rel_path):
            return rel_path
        return os.path.normpath(os.path.join(self.base_dir, rel_path))

    def _locate_metrics_file(self) -> str:
        """Searches candidate locations for metrics.json."""
        candidates = [
            self.resolve_path(os.path.join("sandbox", "out", "metrics.json")),
            self.resolve_path(os.path.join("out", "metrics.json")),
            self.resolve_path("metrics.json")
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
        return None

    def _load_and_validate_metrics(self) -> Tuple[bool, Any, str]:
        """Loads and validates metrics.json against schema."""
        metrics_file = self._locate_metrics_file()
        if not metrics_file:
            return False, None, "metrics.json not found in sandbox/out/, out/, or project directory."

        try:
            with open(metrics_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            return False, None, f"Could not parse {metrics_file}: {e}"

        # Schema validation
        schema_path = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", "_shared", "metrics.schema.json")
        )
        if not os.path.exists(schema_path):
            schema_path = self.resolve_path(os.path.join("_shared", "metrics.schema.json"))

        if jsonschema and os.path.exists(schema_path):
            try:
                with open(schema_path, "r", encoding="utf-8") as sf:
                    schema = json.load(sf)
                jsonschema.validate(instance=data, schema=schema)
            except jsonschema.ValidationError as ve:
                return False, None, f"metrics.json fails schema validation: {ve.message}"
            except Exception as se:
                return False, None, f"Error validating metrics.json schema: {se}"

        return True, data, ""

    def evaluate_assertion(self, assertion_str: str) -> Tuple[bool, str]:
        """
        Parses and evaluates deterministic programmatic assertions.
        """
        assertion_str = assertion_str.strip()

        # 1. file_exists('path')
        m_file = re.match(r"^file_exists\(['\"](.*?)['\"]\)$", assertion_str)
        if m_file:
            path = self.resolve_path(m_file.group(1))
            if os.path.exists(path):
                return True, f"File exists: {m_file.group(1)}"
            return False, f"File does NOT exist: {m_file.group(1)} (resolved: {path})"

        # 2. ast_scanner_passed('path')
        m_ast = re.match(r"^ast_scanner_passed\(['\"](.*?)['\"]\)$", assertion_str)
        if m_ast:
            path = self.resolve_path(m_ast.group(1))
            if not os.path.exists(path):
                return False, f"Cannot scan missing file: {m_ast.group(1)}"
            if Scanner is None:
                return False, "AST Scanner module could not be imported."
            try:
                with open(path, "r", encoding="utf-8") as f:
                    source = f.read()
                tree = ast.parse(source, filename=path)
                scanner = Scanner(filename=path)
                scanner.visit(tree)
                if scanner.violations:
                    return False, f"AST Scanner found {len(scanner.violations)} violation(s) in {m_ast.group(1)}: {scanner.violations}"
                return True, f"AST Scanner passed for {m_ast.group(1)}"
            except Exception as e:
                return False, f"AST Scanner parsing error in {m_ast.group(1)}: {e}"

        # 3. is_single_sklearn_pipeline('path')
        m_pipe = re.match(r"^is_single_sklearn_pipeline\(['\"](.*?)['\"]\)$", assertion_str)
        if m_pipe:
            path = self.resolve_path(m_pipe.group(1))
            if not os.path.exists(path):
                return False, f"Cannot check pipeline: file missing {m_pipe.group(1)}"
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                tree = ast.parse(content, filename=path)
                validator = PipelineASTValidator()
                validator.visit(tree)

                if validator.leakage_violations:
                    return False, f"Pipeline leakage violation: {validator.leakage_violations[0]}"

                total_pipes = validator.pipeline_assignments_count if validator.pipeline_assignments_count > 0 else validator.pipeline_instantiations_count
                if total_pipes == 0:
                    return False, f"No scikit-learn Pipeline construction detected in {m_pipe.group(1)}."
                if total_pipes > 1:
                    return False, f"Multiple pipelines ({total_pipes}) found in {m_pipe.group(1)}; policy requires exactly ONE single scikit-learn pipeline."
                if not validator.pipeline_used_in_fit_or_cv:
                    return False, f"Pipeline defined in {m_pipe.group(1)} is never fitted or evaluated in cross-validation."

                return True, f"Verified single scikit-learn Pipeline construction and usage with no data leakage in {m_pipe.group(1)}."
            except Exception as e:
                return False, f"Error inspecting pipeline AST in {m_pipe.group(1)}: {e}"

        # 4. cv_folds_logged(N)
        m_cv = re.match(r"^cv_folds_logged\((\d+)\)$", assertion_str)
        if m_cv:
            expected_folds = int(m_cv.group(1))
            ok, data, err = self._load_and_validate_metrics()
            if not ok:
                return False, err

            # Extract fold_scores
            fold_scores = []
            if isinstance(data, dict):
                if "fold_scores" in data and isinstance(data["fold_scores"], list):
                    fold_scores = data["fold_scores"]
                elif "models" in data and isinstance(data["models"], list) and len(data["models"]) > 0:
                    fold_scores = data["models"][0].get("fold_scores", [])
                elif "candidates" in data and isinstance(data["candidates"], dict) and len(data["candidates"]) > 0:
                    first_cand = next(iter(data["candidates"].values()))
                    if isinstance(first_cand, dict):
                        fold_scores = first_cand.get("fold_scores", [])

            if not fold_scores:
                return False, "metrics.json does not contain a valid 'fold_scores' array."

            if len(fold_scores) != expected_folds:
                return False, f"Cross-validation fold count mismatch: expected {expected_folds} folds, found {len(fold_scores)} folds in metrics.json."

            return True, f"Cross-validation with {expected_folds} folds verified from metrics.json."

        # 5. assert_1se_rule_applied()
        if assertion_str == "assert_1se_rule_applied()":
            ok, data, err = self._load_and_validate_metrics()
            if not ok:
                return False, f"1-SE verification failed: {err}"

            # Locate evaluation report
            eval_report_path = self.resolve_path(os.path.join("sandbox", "out", "EVALUATION-REPORT.md"))
            if not os.path.exists(eval_report_path):
                eval_report_path = self.resolve_path("EVALUATION-REPORT.md")
            if not os.path.exists(eval_report_path):
                return False, "1-SE rule verification failed: EVALUATION-REPORT.md not found."

            with open(eval_report_path, "r", encoding="utf-8") as f:
                report_text = f.read()

            # Parse selected model from EVALUATION-REPORT.md
            sel_match = re.search(r"Selected Model.*?:?\s*\**([a-zA-Z0-9_\- ]+?)\**(?:\n|\.|\$)", report_text, re.IGNORECASE)
            if not sel_match:
                sel_match = re.search(r"Selected Model[:\s]+([^\n\.,]+)", report_text, re.IGNORECASE)
            if not sel_match:
                return False, "1-SE rule verification failed: 'Selected Model' not found in EVALUATION-REPORT.md."

            selected_model_in_report = sel_match.group(1).strip().strip("*").strip()

            # Case A: metrics.json has candidates dictionary or models list
            candidates = {}
            if isinstance(data, dict):
                if "candidates" in data and isinstance(data["candidates"], dict):
                    candidates = data["candidates"]
                elif "models" in data and isinstance(data["models"], list):
                    for idx, m in enumerate(data["models"]):
                        name = m.get("model") or m.get("name") or f"Model_{idx}"
                        candidates[name] = m

            if candidates:
                # Calculate mean and SE for each candidate
                stats = {}
                for name, cand in candidates.items():
                    scores = cand.get("fold_scores", [])
                    if not scores:
                        continue
                    n = len(scores)
                    mean_val = sum(scores) / n
                    if n > 1:
                        variance = sum((x - mean_val) ** 2 for x in scores) / (n - 1)
                        se = math.sqrt(variance) / math.sqrt(n)
                    else:
                        se = 0.0
                    stats[name] = {
                        "mean": mean_val,
                        "se": se,
                        "complexity": cand.get("complexity", 1)
                    }

                if stats:
                    # Determine whether metric is error (lower is better) or score (higher is better)
                    # Determine whether metric is error (lower is better) or score (higher is better)
                    metrics_metric = (data.get("metric_name") or "").lower()
                    client_metric = (self.data.get("client_grounding", {}).get("business_metric") or "").lower()
                    if any(kw in metrics_metric for kw in ["rmse", "mae", "mse", "loss"]):
                        is_error = True
                    elif any(kw in metrics_metric for kw in ["f1", "acc", "auc", "precision", "recall"]):
                        is_error = False
                    elif any(kw in report_text.lower() for kw in ["rmse", "mae", "mse", "loss"]):
                        is_error = True
                    elif any(kw in client_metric for kw in ["rmse", "mae", "mse", "loss"]):
                        is_error = True
                    else:
                        is_error = False
                    if is_error:
                        best_name = min(stats, key=lambda k: stats[k]["mean"])
                        best_mean = stats[best_name]["mean"]
                        best_se = stats[best_name]["se"]
                        eligible = [k for k, v in stats.items() if v["mean"] <= best_mean + best_se]
                    else:
                        best_name = max(stats, key=lambda k: stats[k]["mean"])
                        best_mean = stats[best_name]["mean"]
                        best_se = stats[best_name]["se"]
                        eligible = [k for k, v in stats.items() if v["mean"] >= best_mean - best_se]

                    expected_1se_model = min(eligible, key=lambda k: stats[k]["complexity"])
                    if expected_1se_model.lower() not in selected_model_in_report.lower() and selected_model_in_report.lower() not in expected_1se_model.lower():
                        return False, f"1-SE rule violation: calculated 1-SE model is '{expected_1se_model}', but EVALUATION-REPORT.md selected '{selected_model_in_report}'."
                    return True, f"1-SE rule verified: '{selected_model_in_report}' correctly selected within 1-SE window of best model '{best_name}'."

            # Case B: Single model logged in metrics.json
            fold_scores = data.get("fold_scores", [])
            if fold_scores:
                n = len(fold_scores)
                mean_val = sum(fold_scores) / n
                variance = sum((x - mean_val) ** 2 for x in fold_scores) / (n - 1) if n > 1 else 0
                se = math.sqrt(variance) / math.sqrt(n) if n > 1 else 0
                model_name = data.get("model", "Model")
                if model_name.lower() in selected_model_in_report.lower() or selected_model_in_report.lower() in model_name.lower():
                    return True, f"1-SE rule verified: single model '{model_name}' logged with SE={se:.4f}."
                return False, f"1-SE rule mismatch: metrics.json model '{model_name}' does not match selected model '{selected_model_in_report}'."

            return False, "1-SE rule could not be verified from metrics data."

        # 6. decision_logged_in_ledger('path')
        m_dec = re.match(r"^decision_logged_in_ledger\(['\"](.*?)['\"]\)$", assertion_str)
        if m_dec:
            path = self.resolve_path(m_dec.group(1))
            if not os.path.exists(path):
                return False, f"Ledger file missing: {m_dec.group(1)}"
            if enforce_ledger is not None:
                ret = enforce_ledger(path, online=False, allow_offline=True)
                if ret != 0:
                    return False, f"Constitution enforcement failed for ledger {m_dec.group(1)} (exit code {ret})."

            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            if parse_tables:
                tables = parse_tables(content)
                ledgers = [t for t in tables if all(h in [x.lower() for x in t[0]] for h in REQUIRED_HEADERS)]
                if not ledgers or len(ledgers[0][1]) == 0:
                    return False, f"Decision ledger {m_dec.group(1)} has no recorded decision rows."
                return True, f"Decision ledger {m_dec.group(1)} passed constitutional check with {len(ledgers[0][1])} logged decisions."

            rows = [line for line in content.splitlines() if line.strip().startswith("|") and "---" not in line and "Stage" not in line]
            if len(rows) > 0:
                return True, f"Decision ledger contains {len(rows)} decision entries."
            return False, f"Decision ledger {m_dec.group(1)} has no recorded decision rows."

        # Fallback unknown assertion
        return False, f"Unknown assertion predicate: {assertion_str}"

    def check_step(self, step_id: str, check_post: bool = True) -> Tuple[bool, List[str]]:
        """Evaluates assertions for a given step."""
        dag = self.data["execution_dag"]
        step = next((s for s in dag if s["step_id"] == step_id), None)
        if not step:
            return False, [f"Step '{step_id}' not found in execution DAG."]

        logs = []
        all_passed = True

        # Pre-conditions
        for prec in step.get("pre_conditions", []):
            passed, msg = self.evaluate_assertion(prec)
            logs.append(f"  [PRE-CONDITION] {'PASS' if passed else 'FAIL'}: {msg}")
            if not passed:
                all_passed = False

        if check_post:
            for postc in step.get("post_assertions", []):
                passed, msg = self.evaluate_assertion(postc)
                logs.append(f"  [POST-ASSERTION] {'PASS' if passed else 'FAIL'}: {msg}")
                if not passed:
                    all_passed = False

        return all_passed, logs

    def get_status(self) -> dict:
        """Returns step-by-step evaluation status across the entire DAG."""
        dag = self.data["execution_dag"]
        status_report = []
        current_active_step = None
        for step in dag:
            step_id = step["step_id"]
            ok, logs = self.check_step(step_id, check_post=True)
            status_report.append({
                "step_id": step_id,
                "stage": step.get("stage"),
                "passed": ok,
                "logs": logs
            })
            if not ok and current_active_step is None:
                current_active_step = step_id

        return {
            "project_id": self.data.get("project_id"),
            "current_active_step": current_active_step or "ALL_STEPS_COMPLETED",
            "steps": status_report
        }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  run_policy.py verify <plan_file>")
        print("  run_policy.py check-step <plan_file> <step_id>")
        print("  run_policy.py status <plan_file>")
        sys.exit(1)

    cmd = sys.argv[1]
    plan_path = sys.argv[2]

    try:
        engine = PolicyEngine(plan_path)

        if cmd == "verify":
            ok = engine.verify_integrity()
            sys.exit(0 if ok else 1)

        elif cmd == "check-step":
            if len(sys.argv) < 4:
                print("Error: step_id required for check-step command.")
                sys.exit(1)
            # First ensure plan is intact
            if not engine.verify_integrity():
                sys.exit(2)
            step_id = sys.argv[3]
            ok, logs = engine.check_step(step_id)
            print(f"Step '{step_id}' Check Results:")
            for l in logs:
                print(l)
            sys.exit(0 if ok else 1)

        elif cmd == "status":
            if not engine.verify_integrity():
                sys.exit(2)
            status = engine.get_status()
            print("==================================================")
            print(f" Project: {status['project_id']}")
            print(f" Active Step: {status['current_active_step']}")
            print("==================================================")
            for s in status["steps"]:
                mark = "[PASS]" if s["passed"] else "[PENDING]"
                print(f"{mark} {s['step_id']} (Stage {s['stage']})")
                for lg in s["logs"]:
                    print(f"   {lg}")
            sys.exit(0)

    except Exception as err:
        print(f"Fatal error in run_policy: {err}", file=sys.stderr)
        sys.exit(1)
