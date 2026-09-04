import uvicorn
from fastapi import FastAPI
from routers.documents import router as document_router

app=FastAPI()
app.include_router(document_router)


if __name__=="__main__":
    uvicorn.run("main:app",host="127.0.0.1",port=8000,reload=True)


