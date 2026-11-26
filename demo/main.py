from fastapi import FastAPI

from demo.schemas.chat import ChatRequest, ChatResponse

app=FastAPI()
@app.post("/comment")
def app_comment(request:ChatRequest)->ChatResponse:

    return ChatResponse(message="操作成功",data={"content":request.content
    ,"rating":request.rating})
