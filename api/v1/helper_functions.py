from sqlalchemy.ext.asyncio import AsyncSession
from db.session import AsyncSessionLocal
from db.session import engine , Base
import asyncio
from fastapi import Depends , HTTPException , status
from datetime import datetime, date ,time
from decimal import Decimal
from uuid import UUID
from sqlalchemy.orm import Session
from models.models import User
from groq import Groq
from core.config import settings


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def chat_groq_model(query : str , context : str) -> str:
    client =Groq(api_key=settings.groq_api_key)
    try:
        response =await client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
            ],
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=False
        )
        answer = response.choices[0].message.content
        return answer
    except Exception as e:
        raise Exception(f"Groq API call failed: {str(e)}")
    