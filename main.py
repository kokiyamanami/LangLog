from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(
    title="LangLog API",
    description="FastAPI application",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "LangLog API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/v1/test")
async def test_endpoint(data: dict):
    return {"received": data}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
