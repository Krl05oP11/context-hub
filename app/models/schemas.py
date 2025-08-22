from pydantic import BaseModel, Field
from typing import Optional, List

class ChatRequest(BaseModel):
    message: str
    session_id: str = Field(default="default-session", description="ID único para agrupar la conversación")
    use_context: bool = Field(default=True, description="Si debe buscar contexto relevante previo")

class ChatResponse(BaseModel):
    response: str
    session_id: str
    context_used: Optional[List[str]] = Field(default=None, description="Fragmentos de contexto recuperados y utilizados")

class SummaryRequest(BaseModel):
    text: str
    session_id: str

class SummaryResponse(BaseModel):
    summary: str
