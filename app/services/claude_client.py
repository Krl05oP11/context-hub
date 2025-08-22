import os
from typing import List
from anthropic import AsyncAnthropic
from app.utils.logger import logger

# 🔥 FORZAR CARGA DE VARIABLES DE ENTORNO 🔥
from dotenv import load_dotenv
import os.path

# Cargar variables de entorno desde el archivo .env en el directorio raíz
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(env_path)  # Cargar específicamente desde esta ruta

# DEBUG: Verificar que se cargó la API key
api_key = os.getenv("ANTHROPIC_API_KEY")
if api_key:
    logger.info("✅ ANTHROPIC_API_KEY cargada correctamente")
else:
    logger.warning("⚠️ ANTHROPIC_API_KEY no encontrada después de load_dotenv()")


class ClaudeClient:
    # Variables de clase (se cargan una vez, singleton pattern)
    _api_key = None
    _model = "claude-sonnet-4-20250514"
    _client = None
    _initialized = False

    def __init__(self):
        """Inicialización perezosa - solo se ejecuta si no está inicializado."""
        if not ClaudeClient._initialized:
            self._initialize_client()

    @classmethod
    def _initialize_client(cls):
        """Inicialización única del cliente Anthropic."""
        if cls._initialized:
            return
            
        cls._api_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Validación crítica: verificar que la API key exista
        if not cls._api_key:
            logger.error("❌ ANTHROPIC_API_KEY no encontrada en variables de entorno")
            raise ValueError("ANTHROPIC_API_KEY no configurada. Agrega al archivo .env")
        
        try:
            cls._client = AsyncAnthropic(api_key=cls._api_key)
            cls._initialized = True
            logger.info(f"✅ Claude Client inicializado con modelo: {cls._model}")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando Claude Client: {str(e)}")
            raise

    async def send_message(self, prompt: str) -> str:
        """Envía un prompt a Claude y devuelve la respuesta."""
        if not self._initialized:
            self._initialize_client()
            
        try:
            message = await self._client.messages.create(
                model=self._model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
            
        except Exception as e:
            logger.error(f"❌ Error llamando a Claude API: {str(e)}")
            raise e

    async def send_message_with_context(self, user_message: str, context: List[str], session_id: str) -> str:
        """Envía un mensaje a Claude con contexto estructurado."""
        if not self._initialized:
            self._initialize_client()
            
        try:
            # Construir el prompt con contexto
            context_str = ""
            if context:
                context_str = "\n\n# --- CONTEXTO RELEVANTE DE CONVERSACIONES PREVIAS ---\n"
                for i, ctx in enumerate(context, 1):
                    context_str += f"{i}. {ctx}\n"
                context_str += "# --- FIN DEL CONTEXTO ---\n\n"

            system_prompt = f"""Eres Claude, un asistente experto en desarrollo de software, IA, y ciencia de datos.
Responde a la pregunta del usuario considerando SERIAMENTE el contexto proporcionado de conversaciones anteriores de esta sesión (Session ID: {session_id}).
Si el contexto no es relevante para la pregunta, ignóralo silenciosamente.
Mantén tus respuestas técnicas, precisas y útiles para un ingeniero senior."""

            full_prompt = f"{system_prompt}\n\n{context_str}# PREGUNTA ACTUAL DEL USUARIO:\n{user_message}"

            # Llamar a la API de Claude
            message = await self._client.messages.create(
                model=self._model,
                max_tokens=4096,
                messages=[{"role": "user", "content": full_prompt}]
            )
            
            return message.content[0].text
            
        except Exception as e:
            logger.error(f"❌ Error llamando a Claude API con contexto: {str(e)}")
            raise e

# Instancia global (patrón singleton) - Se inicializa solo una vez al importar
claude_client = ClaudeClient()
