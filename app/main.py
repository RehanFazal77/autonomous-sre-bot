from fastapi import FastAPI
import os

app = FastAPI()

# A simple health endpoint
@app.get("/")
def read_root():
    return {"status": "ok", "service": "target-app"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
