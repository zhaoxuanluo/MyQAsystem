"""Start backend server."""
import subprocess
import sys
import os

os.chdir(r"f:\1参与项目\知识库\RAGAPP\backend")
subprocess.run([sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"])
