import os
import subprocess

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend = os.path.join(root, "backend")
python = os.path.join(backend, ".venv311", "Scripts", "python.exe")

env = os.environ.copy()
env["CORS_ORIGINS"] = '["http://localhost:3000", "http://127.0.0.1:3000"]'
env["SECRET_KEY"] = env.get("SECRET_KEY") or "change-this-to-a-32-byte-random-secret"
env["APP_ENV"] = "development"
env["LOG_LEVEL"] = "INFO"
env["LLM_PROVIDER"] = "mock"
env["DATABASE_URL"] = f"sqlite:///{os.path.join(backend, 'divyadrishti.db')}"
env["CORPUS_VECTOR_STORE_DIR"] = os.path.join(backend, ".chroma")

log_path = os.path.join(backend, "scripts-logs", "backend.log")
os.makedirs(os.path.dirname(log_path), exist_ok=True)

proc = subprocess.Popen(
    [python, "-m", "uvicorn", "divyadrishti.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
    cwd=os.path.join(backend, "src"),
    env=env,
    stdout=open(log_path, "w", encoding="utf-8"),
    stderr=subprocess.STDOUT,
    stdin=subprocess.DEVNULL,
    creationflags=subprocess.DETACHED_PROCESS,
)
print("started backend pid", proc.pid)
