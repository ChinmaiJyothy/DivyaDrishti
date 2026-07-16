import os
import subprocess
import time

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
nd = os.path.join(root, "tools", "node")
env = os.environ.copy()
env["PATH"] = nd + os.pathsep + env.get("PATH", "")
env["NO_COLOR"] = "1"
env["NEXT_TELEMETRY_DISABLED"] = "1"

log_path = os.path.join(root, "frontend", "scripts-logs", "dev.log")

proc = subprocess.Popen(
    [os.path.join(nd, "node.exe"), os.path.join(root, "frontend", "node_modules", "next", "dist", "bin", "next"), "dev", "-p", "3000"],
    cwd=os.path.join(root, "frontend"),
    env=env,
    stdout=open(log_path, "w", encoding="utf-8"),
    stderr=subprocess.STDOUT,
    stdin=subprocess.DEVNULL,
    creationflags=subprocess.DETACHED_PROCESS,
)
print("started dev server pid", proc.pid)
