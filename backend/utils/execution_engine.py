# backend/utils/execution_engine.py

import subprocess
import time
import psutil
import tempfile
import os
import uuid
from utils.metrics_db import store_metrics

def run_in_warm_container(container_name: str, language: str, code: str):
    try:
        if language == "python":
            cmd = ["docker", "exec", container_name, "python3", "-c", code]
        elif language == "javascript":
            cmd = ["docker", "exec", container_name, "node", "-e", code]
        else:
            return {"error": "Unsupported language for warm execution"}

        start = time.time()

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5
        )

        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().used / (1024 * 1024)

        end = time.time()

        metrics = {
            "duration": end - start,
            "cpu_percent": cpu_usage,
            "memory_mb": round(memory_usage, 2),
            "error": None if result.returncode == 0 else result.stderr.strip()
        }

       

        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode,
            "metrics": metrics
        }

    except subprocess.TimeoutExpired:
        return {"error": "Execution timed out."}
    except Exception as e:
        return {"error": str(e)}
def run_with_runtime(image: str, language: str, code: str, runtime: str = "runc"):
    file_ext = "py" if language == "python" else "js" if language == "javascript" else None
    if file_ext is None:
        return {"error": "Unsupported language"}

    filename = f"temp_{uuid.uuid4().hex}.{file_ext}"

    try:
        with tempfile.TemporaryDirectory() as tmpdirname:
            filepath = os.path.join(tmpdirname, filename)
            with open(filepath, "w") as f:
                f.write(code)

            exec_cmd = f"python {filename}" if language == "python" else f"node {filename}"

            docker_cmd = [
                "docker", "run", "--rm",
                "--runtime", runtime,
                "-v", f"{tmpdirname}:/usr/src/app",
                "-w", "/usr/src/app",
                image, "sh", "-c", exec_cmd
            ]

            start = time.time()
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_usage = psutil.virtual_memory().used / (1024 * 1024)
            result = subprocess.run(docker_cmd, capture_output=True, text=True, timeout=10)
            end = time.time()

            metrics = {
                "duration": end - start,
                "cpu_percent": cpu_usage,
                "memory_mb": round(memory_usage, 2),
                "error": None if result.returncode == 0 else result.stderr.strip()
            }
           

            return {
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "returncode": result.returncode,
                "metrics": metrics
            }

    except subprocess.TimeoutExpired:
        return {"error": "Execution timed out."}
    except Exception as e:
        return {"error": str(e)}

