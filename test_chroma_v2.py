import chromadb
from chromadb.config import Settings

def test_chroma_connection():
    try:
        print("🧪 Probando conexión con ChromaDB API v2...")
        
        client = chromadb.HttpClient(
            host="localhost",
            port=8003,
            settings=Settings(chroma_api_impl="rest")
        )
        
        # Probar heartbeat (endpoint de API v2)
        heartbeat = client.heartbeat()
        print(f"✅ Heartbeat: {heartbeat}")
        
        # Probar listar colecciones
        collections = client.list_collections()
        print(f"✅ Colecciones: {[col.name for col in collections]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_chroma_connection()
