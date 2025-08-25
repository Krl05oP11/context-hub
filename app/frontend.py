import sys
import os
sys.path.append('/home/carlos/Projects/context-hub')

from app.services.context_manager import get_context_manager
import streamlit as st
import requests
import json
from datetime import datetime

context_manager = get_context_manager()
# Configuración de la página
st.set_page_config(
    page_title="ClaudeContextHub - Memoria para Claude",
    page_icon="🧠",
    layout="wide"
)

# Título y descripción
st.title("🧠 ClaudeContextHub v1.0")
st.markdown("""
**Solución de memoria persistente para Claude** - Rompe los límites de contexto con RAG local.
*Versión 1.0 - Funcionalidad básica estable*
""")

# Sidebar para configuración
with st.sidebar:
    st.header("🧠 ClaudeContextHub v1.0")
    st.header("⚙️ Configuración")
    api_url = st.text_input("API URL", value="http://localhost:8006")
    
    # Usar session_id persistente
    SESSION_ID_FIJO = "usuario_carlos"
    session_id = st.text_input("Session ID", value=SESSION_ID_FIJO, disabled=True)
    st.info("💡 Session ID fijo: memoria unificada activada")

    use_context = st.checkbox("Usar contexto", value=True)
    
    st.divider()
    st.info("""
    **Instrucciones:**
    1. Memoria unificada simpre activa
    2. El sistema buscará en TODAS tus conversaciones
    3. Contexto infinito habilitado
    """)

# Inicializar estado de la conversación
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial de mensajes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input de usuario
if prompt := st.chat_input("Escribe tu mensaje para Claude..."):
    # Agregar mensaje de usuario al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Mostrar indicador de progreso
    with st.chat_message("assistant"):
        with st.spinner("Claude está pensando..."):
            try:
                # Llamar a la API de ContextHub
                response = requests.post(
                    f"{api_url}/api/v1/chat",
                    json={
                        "message": prompt,
                        "session_id": session_id,
                        "use_context": use_context
                    },
                    timeout=120
                )
                
                if response.status_code == 200:
                    result = response.json()
                    # Mostrar respuesta
                    st.markdown(result["response"])
                    
                    # Guardar en historial
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": result["response"]
                    })
                
                else:
                    st.error(f"Error en la API: {response.text}")
            
            except requests.exceptions.RequestException as e:
                st.error(f"Error de conexión: {str(e)}")
            except Exception as e:
                st.error(f"Error inesperado: {str(e)}")

# Botones de utilidad en el sidebar
with st.sidebar:
    st.divider()
    if st.button("🔄 Limpiar chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    if st.button("📊 Ver estado del API", use_container_width=True):
        try:
            health_response = requests.get(f"{api_url}/health")
            if health_response.status_code == 200:
                st.success("✅ API saludable")
            else:
                st.error("❌ API no responde")
        except:
            st.error("❌ No se puede conectar a la API")
