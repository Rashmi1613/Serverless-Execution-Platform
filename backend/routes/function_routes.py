from fastapi import APIRouter, HTTPException
from utils.execution_engine import run_in_warm_container, run_with_runtime
from utils.metrics_db import (
    store_metrics,
    get_aggregated_metrics,
    get_runtime_metrics
)
from pydantic import BaseModel
from typing import Optional, Dict

router = APIRouter()

# In-memory database to simulate function metadata
function_registry: Dict[str, dict] = {}

class FunctionExecRequest(BaseModel):
    functionCode: str
    language: str
    runtime: str = "docker"

class FunctionMetadata(BaseModel):
    name: str
    route: str
    language: str
    timeout: Optional[int] = 10

# --- Execution Endpoint ---
@router.post("/execute")
def execute_function(req: FunctionExecRequest):
    code = req.functionCode
    language = req.language.lower()
    runtime = req.runtime.lower()

    if not code:
        raise HTTPException(status_code=400, detail="Function code is required.")

    function_name = "unknown"
    # Try to match a registered function name
    for name, meta in function_registry.items():
        if meta["language"] == language:
            function_name = name
            break

    # Warm container
    if runtime == "docker-warm":
        result = run_in_warm_container("warm-python-fn", language, code)
        store_metrics(function_name, runtime, result["metrics"])
        return result

    # gVisor simulation with runc (since WSL2 doesn't support runsc)
    elif runtime == "gvisor":
        result = run_with_runtime("python-lambda-runtime", language, code, runtime="runsc")
        store_metrics(function_name, runtime, result["metrics"])
        return result

    # Cold Docker (default)
    elif runtime == "docker":
        result = run_with_runtime("python-lambda-runtime", language, code, runtime="runc")
        store_metrics(function_name, runtime, result["metrics"])
        return result

    else:
        raise HTTPException(status_code=400, detail="Unsupported runtime specified.")

# --- Register Function ---
@router.post("/register")
def register_function(meta: FunctionMetadata):
    if meta.name in function_registry:
        raise HTTPException(status_code=400, detail="Function already exists.")
    function_registry[meta.name] = meta.dict()
    return {"message": f"Function '{meta.name}' registered successfully."}

# --- Get Function Metadata ---
@router.get("/get/{name}")
def get_function(name: str):
    if name not in function_registry:
        raise HTTPException(status_code=404, detail="Function not found.")
    return function_registry[name]

# --- List All Functions ---
@router.get("/list")
def list_functions():
    return function_registry

# --- Update Function ---
@router.put("/update/{name}")
def update_function(name: str, meta: FunctionMetadata):
    if name not in function_registry:
        raise HTTPException(status_code=404, detail="Function not found.")
    function_registry[name] = meta.dict()
    return {"message": f"Function '{name}' updated."}

# --- Delete Function ---
@router.delete("/delete/{name}")
def delete_function(name: str):
    if name not in function_registry:
        raise HTTPException(status_code=404, detail="Function not found.")
    del function_registry[name]
    return {"message": f"Function '{name}' deleted successfully."}
    

@router.get("/metrics/{name}")
def get_metrics(name: str):
    return get_aggregated_metrics(name)
    
@router.get("/runtime-metrics")
def runtime_metrics():
    return get_runtime_metrics()
