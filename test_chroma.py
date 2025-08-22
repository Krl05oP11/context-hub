import chromadb
from chromadb.config import Settings

try:
    client = chromadb.HttpClient(
        host="localhost",
        port=8003,
        settings=Settings(chroma_api_impl="rest", anonymized_telemetry=False)
    )
    
    print("✅ Heartbeat:", client.heartbeat())
    print("✅ Version:", client.get_version())
    print("✅ Conexión exitosa!")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
