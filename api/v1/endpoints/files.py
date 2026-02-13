from fastapi import APIRouter , Depends , UploadFile , File , HTTPException , status 
from datetime import datetime , timezone
import aiofiles
import os
from sqlalchemy.ext.asyncio import AsyncSession
from ..dependencies import get_async_db , get_current_user
from models.models import Document,User
from sqlalchemy import select


router=APIRouter()

@router.post("/uploadDoc")
async def upload_doc(db:AsyncSession = Depends(get_async_db) ,file : UploadFile=File(...) , current_user = Depends(get_current_user)):
    try:
        allowed_file_types = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']
        
        if file.content_type not in allowed_file_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type, only allowed: {allowed_file_types}"
            )
        
        file_content = await file.read()
        file_size = len(file_content)
        
        upload_dir = "uploads"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        file_name = f"{current_user.user_id}_{datetime.now(timezone.utc).timestamp()}_{file.filename}"
        file_path = os.path.join(upload_dir, file_name)
        
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(file_content)
        
        new_document = Document(
            user_id=current_user.user_id,
            file_size=str(file_size),
            file_path=file_path,
            upload_time = datetime.now(timezone.utc)
        )
        
        db.add(new_document)
        await db.commit()  
        await db.refresh(new_document)  
        
        return {
            "message": "File uploaded successfully",
            "file_name": file.filename,
            "file_size": file_size,
            "file_path": file_path,
            "upload_time": new_document.upload_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()  
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )
    

@router.post("/showDocuments")
async def show_all_documents(current_user : User = Depends(get_current_user) , db : AsyncSession = Depends(get_async_db)):
    result =await db.execute(select(Document).where(Document.user_id == current_user.user_id))

    user_documents = result.scalars().all()

    return [
        {
            "file_id": doc.file_id,
            "user_id": doc.user_id,
            "file_size": doc.file_size,
            "file_path": doc.file_path,
            "upload_time": str(doc.upload_time)
        }
        for doc in user_documents
    ]


