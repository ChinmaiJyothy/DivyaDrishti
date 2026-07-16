"""Build helper that runs frontend npm commands from the project root."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(
    cwd: Path,
    cmd: list[str],
    env: dict[str, str],
    log_dir: Path,
) -> subprocess.CompletedProcess[str]:
    label = "_".join(cmd)
    log_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = log_dir / f"{label}.stdout.log"
    stderr_path = log_dir / f"{label}.stderr.log"

    print(f"\n==== Running: {' '.join(cmd)} (cwd: {cwd}) ====")
    if sys.platform == "win32":
        cmd = ["cmd", "/c"] + cmd
    result = subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    stdout_path.write_text(result.stdout or "", encoding="utf-8")
    stderr_path.write_text(result.stderr or "", encoding="utf-8")

    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip(), file=sys.stderr)

    if result.returncode != 0:
        print(f"FAILED: {' '.join(cmd)} (exit code {result.returncode})")
        print(f"  stdout log: {stdout_path}")
        print(f"  stderr log: {stderr_path}")
        raise SystemExit(result.returncode)

    print(f"OK: {' '.join(cmd)}")
    return result


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    frontend = root / "frontend"
    node_dir = root / "tools" / "node"
    log_dir = frontend / "scripts-logs"

    if not node_dir.exists():
        print(f"Node.js not found at {node_dir}", file=sys.stderr)
        raise SystemExit(1)

    env = os.environ.copy()
    env["PATH"] = str(node_dir) + os.pathsep + env.get("PATH", "")
    env["NODE_ENV"] = "development"
    env["CI"] = "true"
    env["NEXT_TELEMETRY_DISABLED"] = "1"

    # Ensure local env is set for builds.
    env_example = frontend / ".env.example"
    env_local = frontend / ".env.local"
    if env_example.exists() and not env_local.exists():
        shutil.copy(env_example, env_local)
        print(f"Copied {env_example} to {env_local}")

    # Read package.json to decide on the typecheck script.
    package_json = json.loads((frontend / "package.json").read_text(encoding="utf-8"))
    scripts = package_json.get("scripts", {})

    # npm install
    run_command(frontend, ["npm", "install", "--no-progress", "--loglevel=error"], env, log_dir)

    # lint
    run_command(frontend, ["npm", "run", "lint"], env, log_dir)

    # typecheck: prefer package.json script, else run tsc directly.
    if "typecheck" in scripts:
        run_command(frontend, ["npm", "run", "typecheck"], env, log_dir)
    else:
        run_command(frontend, ["npx", "tsc", "--noEmit"], env, log_dir)

    # tests: use the non-interactive run target to avoid hanging on watch mode.
    if "test:run" in scripts:
        run_command(frontend, ["npm", "run", "test:run"], env, log_dir)
    else:
        run_command(frontend, ["npm", "run", "test"], env, log_dir)

    # production build
    build_env = env.copy()
    build_env["NODE_ENV"] = "production"
    run_command(frontend, ["npm", "run", "build"], build_env, log_dir)

    print("\n==== Frontend build pipeline succeeded ====")


if __name__ == "__main__":
    main()
