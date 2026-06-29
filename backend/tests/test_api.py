import requests

BASE_URL = "http://127.0.0.1:8000"

def test_execute_function():
    response = requests.post(
        f"{BASE_URL}/functions/execute",
        json={
            "functionCode": "print('Lambda Execution Works!')",
            "language": "python"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "stdout" in data
    assert data["stdout"].strip() == "Lambda Execution Works!"

