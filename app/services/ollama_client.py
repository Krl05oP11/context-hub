import aiohttp
import json
from app.utils.logger import logger
import os
from typing import Optional

class OllamaClient:
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.embeddings_model = os.getenv("EMBEDDINGS_MODEL", "nomic-embed-text")
        self.summary_model = os.getenv("SUMMARY_MODEL", "llama3.1:8b")

    async def get_embeddings(self, text: str) -> list[float]:
        """Obtiene los embeddings para un texto usando el modelo especializado."""
        url = f"{self.base_url}/api/embeddings"
        payload = {"model": self.embeddings_model, "prompt": text}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("embedding", [])
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Error getting embeddings: {response.status} - {error_text}")
                        return []
        except Exception as e:
            logger.error(f"❌ Exception getting embeddings: {str(e)}")
            return []

    async def generate_summary(self, text: str, session_id: str) -> Optional[str]:
        """Usa un LLM local para generar un resumen conciso."""
        prompt = f"""
        Eres un asistente especializado en resumir conversaciones técnicas de desarrollo y IA.
        
        SESSION ID: {session_id}
        
        INSTRUCCIONES:
        1. Analiza el siguiente historial de conversación
        2. Extrae los puntos técnicos más importantes
        3. Identifica decisiones de arquitectura clave
        4. Destaca snippets de código relevantes
        5. Resume problemas y soluciones planteadas
        6. Máximo 150 palabras, estilo conciso y técnico
        
        No incluyas saludos o explicaciones. Solo el resumen puro.
        
        HISTORIAL DE CONVERSACIÓN:
        {text}
        """
        
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.summary_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,  # Baja temperatura para resúmenes precisos
                "top_p": 0.9,
                "num_ctx": 4096
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("response", "").strip()
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Error generating summary: {response.status} - {error_text}")
                        return None
        except Exception as e:
            logger.error(f"❌ Exception generating summary: {str(e)}")
            return None

    async def test_connection(self) -> bool:
        """Testea la conexión con el servidor Ollama."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    return response.status == 200
        except Exception:
            return False

# Instancia global
ollama_client = OllamaClient()
