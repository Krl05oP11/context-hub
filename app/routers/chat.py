from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest
from app.services.claude_client import claude_client
from app.services.context_manager import context_manager
from app.utils.logger import logger

router = APIRouter()

@router.post("/chat")
async def chat_with_context(request: ChatRequest):
    try:
        context_messages = []
        context_used = False
        
        # OBTENER CONTEXTO SI ESTÁ HABILITADO
        if request.use_context and context_manager.is_connected():
            try:
                context_messages = await context_manager.get_relevant_context(
                    session_id=request.session_id,
                    query=request.message,
                    n_results=3  # Número de contextos a recuperar
                )
                context_used = len(context_messages) > 0
                
                logger.info(f"🔍 Contexto encontrado: {len(context_messages)} mensajes para sesión '{request.session_id}'")
                
            except Exception as context_error:
                logger.error(f"⚠️ Error obteniendo contexto: {str(context_error)}")
                # Continuar sin contexto si hay error
                context_messages = []
        
        # CONSTRUIR MENSAJE CON CONTEXTO
        full_message = request.message
        if context_messages:
            context_str = "\n\n--- CONTEXTO DE CONVERSACIONES ANTERIORES ---\n"
            context_str += "\n---\n".join(context_messages)
            context_str += f"\n\n--- PREGUNTA ACTUAL ---\n"
            full_message = context_str + request.message
        
        # OBTENER RESPUESTA DE CLAUDE (CORREGIDO: send_message en lugar de chat)
        response = await claude_client.send_message(
            prompt=full_message
        )
        
        # ALMACENAR INTERACCIÓN SI EL CONTEXTO ESTÁ HABILITADO
        if request.use_context and context_manager.is_connected():
            try:
                await context_manager.add_interaction(
                    session_id=request.session_id,
                    user_message=request.message,
                    ai_response=response
                )
                logger.info(f"💾 Interacción almacenada para sesión '{request.session_id}'")
            except Exception as store_error:
                logger.error(f"⚠️ Error almacenando interacción: {str(store_error)}")
        
        return {
            "response": response,
            "session_id": request.session_id,
            "context_used": context_used,
            "context_count": len(context_messages)
        }
        
    except Exception as e:
        logger.error(f"❌ Error en chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Endpoint de health check"""
    return {
        "status": "healthy",
        "chroma_connected": context_manager.is_connected(),
        "claude_configured": claude_client.is_configured()
    }


@router.get("/sessions")
async def get_sessions():
    """Obtiene todas las sesiones disponibles"""
    try:
        if context_manager.is_connected():
            sessions = await context_manager.get_all_sessions()
            return {"sessions": sessions, "count": len(sessions)}
        else:
            return {"sessions": [], "count": 0, "error": "ChromaDB not connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
