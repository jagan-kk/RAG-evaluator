from fastapi import APIRouter,UploadFile,File

router=APIRouter(
    prefix='/documents',
    tags="Documents"
)

@router.post("/uploads")
async def uploads(file:UploadFile=File(...)):
    return {
        "file_name":file.filename,
        "content_type":file.content_type
    }
