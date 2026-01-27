from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.student import qa as student_qa, survey as student_survey
from app.api.teacher import dashboard, survey as teacher_survey
from app.config import validate_config

# 验证配置
config_valid, config_error = validate_config()
if not config_valid:
    print(f"配置错误: {config_error}")
    # 在开发环境中，即使配置无效也继续运行
    # 在生产环境中，这里应该直接退出

app = FastAPI(
    title="智能教学平台 API",
    description="智能教学平台后端服务",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(student_qa.router, prefix="/api/student/qa", tags=["学生-问答"])
app.include_router(student_survey.router, prefix="/api/student/surveys", tags=["学生-问卷"])
app.include_router(dashboard.router, prefix="/api/teacher/dashboard", tags=["教师-看板"])
app.include_router(teacher_survey.router, prefix="/api/teacher/surveys", tags=["教师-问卷"])

@app.get("/")
async def root():
    return {
        "message": "智能教学平台 API",
        "version": "1.0.0",
        "docs": "/docs",
        "config_status": "ok" if config_valid else "error"
    }

@app.get("/health")
async def health_check():
    return {"status": "ok", "config_status": "ok" if config_valid else "error"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
