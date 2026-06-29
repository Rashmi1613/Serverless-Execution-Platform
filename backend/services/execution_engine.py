import subprocess

def run_function_in_docker(function_code):
    with open("docker/python_runtime/function.py", "w") as f:
        f.write(function_code)
    
    subprocess.run(["docker", "build", "-t", "lambda_function", "docker/python_runtime/"])
    
    try:
        result = subprocess.run(
            ["docker", "run", "--rm", "lambda_function"],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        return "Function execution timed out"

