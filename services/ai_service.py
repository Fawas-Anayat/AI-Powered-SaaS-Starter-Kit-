from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os
import uuid
from typing import List, Dict
from core.config import settings
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.models import Document

class DocumentProcessor:

    def __init__(self):
        self.embeddings =HuggingFaceEmbeddings(
            model_name = settings.MODEL_NAME,
            model_kwargs ={'device' : 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

        os.makedirs(settings.CHROMA_DB_DIR, exist_ok=True)


async def load_document(self, file_path: str, file_type: str) -> List:
        if file_type == "application/pdf":
            loader = PyPDFLoader(file_path)
            
        elif file_type == "docx":
            loader = Docx2txtLoader(file_path)
            
        elif file_type == "txt":
            loader = TextLoader(file_path, encoding='utf-8')
            
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        

        #after the await we can only write the async functions not the sync ones and in the  case we have the sync functions then we should use the thread pool

        documents =await asyncio.to_thread(loader.load)
        
        return documents

async def store_in_normal_db(self , file_id : int , collection_name : str , chunk_count : int , db: AsyncSession):
    try:
        result = await db.execute(select(Document).where(Document.file_id == file_id))

        document = result.scalar_one_or_none()

        if not document:
                raise ValueError(f"Document with id {file_id} not found")
        
        document.collection_name = collection_name
        document.chunk_count = chunk_count
        document.processing_status = "completed"

        await db.commit()
        await db.refresh(document)

    except Exception as e:
        await db.rollback()
        raise

async def process_and_store_in_chromadb(self , file_path :str ,file_type : str ,user_id :int ,file_id :int , db:AsyncSession ):
    try:
        documents = self.load_document(file_path , file_type)

        chunks = self.text_splitter.split_documents(documents)

        for i, chunk in enumerate(chunks):
                    chunk.metadata.update({
                        'user_id': user_id,
                        'document_id': file_id,
                        'chunk_index': i,
                        'source': file_path
                    })

        collection_name = f"user_{user_id}_doc_{file_id}_{uuid.uuid4().hex[:8]}"

        vector_store = Chroma.from_documents(
                    documents=chunks,
                    embedding=self.embeddings,
                    collection_name=collection_name,
                    persist_directory=settings.CHROMA_DB_DIR
                )
        
        stored_count = vector_store._collection.count()

        self.store_in_db(
                    file_id=file_id,
                    collection_name=collection_name,
                    chunk_count=len(chunks),
                    db=db
                )
        
        return {
                    "file_id " : file_id,
                    "collection_name": collection_name,
                    "chunk_count": len(chunks),
                    "embedding_dimension": settings.EMBEDDING_DIMENSION
                }
    
    except Exception as e:
            raise Exception(f"Failed to process document: {str(e)}")
    



     


