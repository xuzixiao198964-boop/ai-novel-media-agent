from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.api import auth, tasks, novels, videos, admin_simple, users, payments

app = FastAPI(
    title="AI Novel Media Agent API",
    description="AI驱动的小说创作和媒体内容生成平台",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由 - 添加/api前缀
app.include_router(auth.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(novels.router, prefix="/api/novels", tags=["novels"])
app.include_router(videos.router, prefix="/api/videos", tags=["videos"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])
app.include_router(admin_simple.router)

@app.on_event("startup")
async def startup_event():
    init_db()
    print("Database initialized")

@app.get("/")
async def root():
    return {
        "message": "AI Novel Media Agent API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/health")
async def api_health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
