import uvicorn
from fastapi import FastAPI
from routers.documents import router as document_router
from routers.chat import router as chat_router
from routers.evaluation import router as evaluation_router
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
    allow_origins=["*"]
)

app.include_router(document_router)
app.include_router(chat_router)
app.include_router(evaluation_router)



if __name__=="__main__":
    uvicorn.run("main:app",host="127.0.0.1",port=8000,reload=True)


