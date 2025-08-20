from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utils.logger import logger

app = FastAPI(
    title="ContextHub API",
    description="API para gestionar contexto de conversaciones con Claude",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8503"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "ContextHub API está funcionando correctamente."}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "context-hub-api"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Iniciando servidor ContextHub API...")
    uvicorn.run(app, host="0.0.0.0", port=8004)
