from dotenv import load_dotenv
load_dotenv()  # ← Esta línea debe estar al inicio

# Añade esta importación al inicio de app/main.py
from app.routers import chat
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utils.logger import logger
# Nueva importación
from app.routers import chat

app = FastAPI(
    title="ContextHub API",
    description="API para gestionar contexto de conversaciones con Claude",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8503", "http://localhost:8005"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# nueva línea
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])

@app.get("/")
async def root():
    return {"message": "ContextHub API está funcionando correctamente."}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "context-hub-api"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Iniciando servidor ContextHub API...")
    uvicorn.run(app, host="0.0.0.0", port=8006)
