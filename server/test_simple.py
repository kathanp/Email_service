from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Simple test working!"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "Simple health check"} 