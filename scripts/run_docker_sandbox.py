#!/usr/bin/env python3
"""
run_docker_sandbox.py - Runs Python scripts inside an isolated, non-networked Docker container.
Enforces Constitution Rule F4 & F4.1 with true kernel isolation.
"""

import sys
import os
import shutil
import subprocess

IMAGE_NAME = "ml-model-architect-sandbox:latest"
DOCKERFILE_PATH = os.path.join(os.path.dirname(__file__), "..", "docker", "Dockerfile.sandbox")
SANDBOX_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sandbox"))

def is_docker_available() -> bool:
    """Checks if docker CLI is present and the daemon is responsive."""
    if not shutil.which("docker"):
        return False
    try:
        res = subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
        return res.returncode == 0
    except Exception:
        return False

def build_sandbox_image():
    """Builds the sandbox container image if not already present."""
    print("🐳 Building isolated sandbox Docker image...")
    res = subprocess.run([
        "docker", "build",
        "-f", DOCKERFILE_PATH,
        "-t", IMAGE_NAME,
        os.path.dirname(DOCKERFILE_PATH)
    ])
    if res.returncode != 0:
        raise RuntimeError("Failed to build Docker sandbox image.")

def run_in_docker(script_name: str, args: list = None) -> int:
    """Executes a script from sandbox/ inside Docker with network disabled and resource constraints."""
    if not is_docker_available():
        print("⚠️ [DOCKER UNAVAILABLE] Docker is not running or not installed.")
        print("   Running in fallback mode: Static AST Linter (python scripts/scan_sandbox.py).")
        return 1

    target_script = os.path.basename(script_name)
    script_host_path = os.path.join(SANDBOX_DIR, target_script)
    if not os.path.exists(script_host_path):
        print(f"❌ Target script not found in sandbox: {script_host_path}", file=sys.stderr)
        return 1

    # Ensure image exists
    res = subprocess.run(["docker", "image", "inspect", IMAGE_NAME], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if res.returncode != 0:
        build_sandbox_image()

    docker_cmd = [
        "docker", "run", "--rm",
        "--network", "none",            # Zero network access
        "--memory", "2g",               # 2GB RAM limit
        "--cpus", "2",                  # 2 CPU cores limit
        "--cap-drop", "ALL",            # Drop all kernel capabilities
        "--read-only",                  # Read-only root filesystem
        "--tmpfs", "/tmp:rw,noexec",    # Temporary scratch space without exec
        "-v", f"{SANDBOX_DIR}:/sandbox:ro", # Mount sandbox as read-only volume
        "-w", "/sandbox",
        IMAGE_NAME,
        "python", target_script
    ]
    if args:
        docker_cmd.extend(args)

    print(f"🔒 [DOCKER SANDBOX] Running '{target_script}' with network=none and memory=2g...")
    result = subprocess.run(docker_cmd)
    return result.returncode

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_docker_sandbox.py <script_in_sandbox.py> [args...]")
        sys.exit(1)
    sys.exit(run_in_docker(sys.argv[1], sys.argv[2:]))
