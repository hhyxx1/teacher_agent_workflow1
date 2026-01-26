import os
import sys
from fastapi import FastAPI
from backend.app.api import qa

# 添加 backend/app 到路径以便内部模块可以互相引用
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(
    title="Teacher Agent Workflow API",
    description="基于 LangGraph 的智能助教工作流后端",
    version="1.0.0"
)

# 注册路由
app.include_router(qa.router)

@app.get("/")
async def root():
    return {"message": "Teacher Agent Workflow API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
