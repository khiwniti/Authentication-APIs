import uvicorn
import os

if __name__ == "__main__":
    os.environ["ENVIRONMENT"] = "development"
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    ) 