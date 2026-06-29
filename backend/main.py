from fastapi import FastAPI
from routes.function_routes import router as function_router 
from utils.container_pool import start_warm_containers
from utils.metrics_db import init_db
import sqlite3
from pydantic import BaseModel

app = FastAPI()

@app.on_event("startup")
def warm_up():
    init_db()  
    start_warm_containers()  

@app.get("/")
def read_root():
    return {"message": "Lambda Function API is running!"}

app.include_router(function_router, prefix="/functions")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

