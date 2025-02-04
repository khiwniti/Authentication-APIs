import uvicorn
import os
import multiprocessing

if __name__ == "__main__":
    workers = multiprocessing.cpu_count() * 2 + 1
    os.environ["ENVIRONMENT"] = "production"
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        workers=workers,
        proxy_headers=True,
        forwarded_allow_ips="*",
        log_level="info"
    ) 