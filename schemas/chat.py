from pydantic import BaseModel

class ChatRequest(BaseModel):
    document_id: int
    query: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": 5,
                "query": "What is machine learning?"
            }
        }