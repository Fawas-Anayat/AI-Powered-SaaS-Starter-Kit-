from fastapi import APIRouter , Depends , HTTPException
from models.models import User
from ..dependencies import get_current_user , get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from schemas.chat import ChatRequest
from models.models import Document
from services.ai_service import document_processor
from ..helper_functions import chat_groq_model

router = APIRouter()

@router.post("/chat")
async def chat(request :ChatRequest ,  current_user : User = Depends(get_current_user) , db : AsyncSession = Depends(get_async_db)):
    result =await db.execute(select(Document).where(request.document_id == Document.file_id))
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found or not ready"
        )
    
    if document.processing_status != "completed":
       doc_metadata =await document_processor.process_and_store_in_chromadb(document.file_path ,document.content_type,document.user_id , document.file_id,db=db)
       await document_processor.store_in_normal_db(file_id=doc_metadata["file_id"] , collection_name=doc_metadata["collection_name"] ,chunk_count=doc_metadata["chunk_count"],db=db)
       
    
    vector_store =await document_processor.get_vector_store(document.collection_name)

    relevant_chunks =await vector_store.similarity_search(
        query=request.query,  
        k=5  
    )

    context = "\n\n".join([chunk.page_content for chunk in relevant_chunks])


    prompt = f"""
    You are a helpful assistant. Answer the question based on the context below.
    
    Context from document '{document.file_id}':
    {context}
    
    Question: {request.query}
    
    Answer: Provide a helpful answer based only on the context above. 
    If the answer is not in the context, say "I cannot find this information in the document."
    """

    llm_response =await chat_groq_model(prompt , context)

    return {
        "query": request.query,
        "answer": llm_response,
        "source_document": document.file_id,
        "relevant_chunks_count": len(relevant_chunks),
        "chunks_used": [
            {
                "content": chunk.page_content[:200] + "...", 
                "chunk_index": chunk.metadata.get('chunk_index'),
                "relevance_score": chunk.metadata.get('score', 'N/A')
            }
            for chunk in relevant_chunks
        ]
    }


