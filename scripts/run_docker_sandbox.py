#!/usr/bin/env python3
"""
run_docker_sandbox.py - Runs Python scripts inside an isolated, non-networked Docker container.
Enforces Constitution Rules F4 & F4.1 with true kernel and container isolation.
"""

import argparse
import os
import shutil
import subprocess
import sys

IMAGE_NAME = "ml-model-architect-sandbox:latest"
DOCKERFILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docker", "Dockerfile.sandbox"))
SANDBOX_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sandbox"))
DEFAULT_TIMEOUT = int(os.environ.get("MLA_DOCKER_TIMEOUT", "600"))


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


def run_in_docker(script_name: str, args: list = None, timeout: int = DEFAULT_TIMEOUT) -> int:
    """
    Executes a script from sandbox/ inside Docker with network disabled,
    read-only root/sandbox mounts, writable sandbox/out mount, and resource constraints.
    """
    if not is_docker_available():
        print("❌ [DOCKER UNAVAILABLE] Docker is not installed or the Docker daemon is not running.", file=sys.stderr)
        print("   To install Docker, visit: https://docs.docker.com/get-docker/", file=sys.stderr)
        print("   On Linux: sudo systemctl start docker", file=sys.stderr)
        print("   On Windows/macOS: Start Docker Desktop.", file=sys.stderr)
        return 1

    target_script = os.path.basename(script_name)
    script_host_path = os.path.join(SANDBOX_DIR, target_script)
    if not os.path.exists(script_host_path):
        print(f"❌ Target script not found in sandbox: {script_host_path}", file=sys.stderr)
        return 1

    # Ensure writable output directory exists
    out_dir = os.path.join(SANDBOX_DIR, "out")
    os.makedirs(out_dir, exist_ok=True)

    # Ensure image exists
    res = subprocess.run(["docker", "image", "inspect", IMAGE_NAME], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if res.returncode != 0:
        build_sandbox_image()

    docker_cmd = [
        "docker", "run", "--rm",
        "--network", "none",                    # Zero network access
        "--memory", "2g",                       # 2GB RAM limit
        "--cpus", "2",                          # 2 CPU cores limit
        "--pids-limit", "100",                  # Prevent fork bombs
        "--security-opt", "no-new-privileges",  # Disallow privilege escalation
        "--user", "1000",                       # Run as non-privileged user
        "--read-only",                          # Read-only root filesystem
        "--tmpfs", "/tmp:rw,noexec",            # Temporary scratch space without exec
        "-v", f"{SANDBOX_DIR}:/sandbox:ro",     # Mount sandbox directory read-only
        "-v", f"{out_dir}:/sandbox/out:rw",     # Mount out directory as writable
        "-w", "/sandbox",
        IMAGE_NAME,
        "python", target_script
    ]
    if args:
        docker_cmd.extend(args)

    print(f"🔒 [DOCKER SANDBOX] Running '{target_script}' (timeout={timeout}s, network=none, memory=2g)...")
    try:
        result = subprocess.run(docker_cmd, timeout=timeout)
        return result.returncode
    except subprocess.TimeoutExpired:
        print(f"🚨 [TIMEOUT] Script execution exceeded wall-clock limit of {timeout}s.", file=sys.stderr)
        return 124


def main():
    parser = argparse.ArgumentParser(description="Run Python scripts inside hardened Docker sandbox.")
    parser.add_argument("script", help="Script inside sandbox/ to execute.")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Wall-clock timeout in seconds (default: 600s)")
    parser.add_argument("args", nargs=argparse.REMAINDER, help="Additional arguments passed to the script.")
    parsed = parser.parse_args()

    sys.exit(run_in_docker(parsed.script, parsed.args, timeout=parsed.timeout))


if __name__ == "__main__":
    main()
