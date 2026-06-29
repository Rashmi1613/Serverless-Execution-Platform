from backend.services.execution_engine import run_function_in_docker

def test_python_execution():
    function_code = 'print("Test Function")'
    output = run_function_in_docker(function_code)
    assert "Test Function" in output
