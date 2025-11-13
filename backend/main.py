"""
菜根日记 FastAPI 主应用
统一的API服务，包含公共接口和管理接口
"""
from fastapi import FastAPI, Query, HTTPException, Depends, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Optional, List
import os
from dotenv import load_dotenv
import secrets

from database import DiaryDatabase
from models import (
    DiaryEntry, DiaryCreate, DiaryUpdate, BatchCreateRequest, 
    BatchCreateResponse, Statistics
)

# Load environment variables
load_dotenv()

# Configuration
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
API_KEY = os.getenv("API_KEY", "your_secret_api_key")
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/diaries.db")
PORT = int(os.getenv("PORT", 8005))

# Initialize FastAPI app
app = FastAPI(
    title="菜根日记存档 API",
    description="南京大学图书馆菜根日记存档系统的API接口",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db = DiaryDatabase(DATABASE_PATH)

# Security
security = HTTPBasic()


# ==================== 依赖项 ====================

def verify_api_key(x_api_key: str = Header(..., description="API密钥")):
    """验证API密钥"""
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的API密钥"
        )
    return x_api_key


def verify_admin_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """验证管理员凭据"""
    is_username_correct = secrets.compare_digest(
        credentials.username.encode("utf8"), ADMIN_USERNAME.encode("utf8")
    )
    is_password_correct = secrets.compare_digest(
        credentials.password.encode("utf8"), ADMIN_PASSWORD.encode("utf8")
    )
    
    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


# ==================== 公共接口（无需鉴权） ====================

@app.get("/", tags=["根路径"])
async def root():
    """API根路径"""
    return {
        "message": "菜根日记存档 API",
        "version": "2.0.0",
        "documentation": "/docs",
        "endpoints": {
            "公共接口": {
                "/api/entries": "查询日记",
                "/api/stats": "统计信息",
                "/api/search": "搜索日记"
            },
            "管理接口（需要API Key）": {
                "/api/admin/entries": "批量添加日记"
            },
            "管理接口（需要登录）": {
                "/api/admin/entries": "管理端查询",
                "/api/admin/entries/{id}": "更新/删除日记"
            }
        }
    }


@app.get("/api/entries", response_model=List[DiaryEntry], tags=["公共接口"])
async def get_entries(
    date: Optional[str] = Query(None, description="按日期筛选 (YYYY-MM-DD)"),
    month: Optional[str] = Query(None, description="按月份筛选 (YYYY-MM)"),
    limit: int = Query(100, ge=1, le=500, description="返回条数"),
    offset: int = Query(0, ge=0, description="偏移量")
):
    """
    查询日记条目
    
    - **date**: 按日期筛选 (YYYY-MM-DD)
    - **month**: 按月份筛选 (YYYY-MM)
    - **limit**: 返回条数 (默认100，最大500)
    - **offset**: 偏移量，用于分页
    """
    try:
        if date:
            entries = db.get_entries_by_date(date)
        elif month:
            year, month_num = map(int, month.split('-'))
            entries = db.get_entries_by_month(year, month_num)
        else:
            entries = db.get_all_entries(limit=limit, offset=offset)
        
        return entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@app.get("/api/stats", response_model=Statistics, tags=["公共接口"])
async def get_statistics():
    """
    获取统计信息
    
    返回：
    - 总条目数
    - 日期范围
    - 每月条目数
    """
    try:
        stats = db.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@app.get("/api/search", response_model=List[DiaryEntry], tags=["公共接口"])
async def search_entries(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    limit: int = Query(50, ge=1, le=200, description="返回条数")
):
    """
    搜索日记内容
    
    - **q**: 搜索关键词（必填）
    - **limit**: 返回条数
    """
    try:
        entries = db.search_entries(q, limit=limit)
        return entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@app.get("/api/dates", tags=["公共接口"])
async def get_available_dates():
    """获取所有可用日期及条目数"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT date, COUNT(*) as count
            FROM diaries
            GROUP BY date
            ORDER BY date DESC
        """)
        
        dates = [{"date": row["date"], "count": row["count"]} for row in cursor.fetchall()]
        conn.close()
        
        return dates
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@app.get("/api/random", response_model=List[DiaryEntry], tags=["公共接口"])
async def get_random_entries(
    count: int = Query(5, ge=1, le=20, description="随机条目数")
):
    """
    获取随机日记条目
    
    - **count**: 随机返回的条目数
    """
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM diaries
            ORDER BY RANDOM()
            LIMIT ?
        """, (count,))
        
        entries = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


# ==================== 管理接口（API Key鉴权） ====================

@app.post("/api/admin/entries", response_model=BatchCreateResponse, tags=["管理接口（API Key）"])
async def batch_create_entries(
    request: BatchCreateRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    批量添加日记条目（需要API Key）
    
    在请求头中添加：X-Api-Key: your_api_key
    
    返回信息：
    - total: 总条数
    - success: 成功添加条数
    - duplicate: 重复条数
    - failed: 失败条数
    - details: 详细信息列表
    """
    try:
        # 转换为数据库需要的格式
        entries = [{"date": e.date, "content": e.content} for e in request.entries]
        result = db.insert_many(entries)
        
        return BatchCreateResponse(
            total=result["total"],
            success=result["success"],
            duplicate=result["duplicate"],
            failed=result["failed"],
            details=result["details"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量添加失败: {str(e)}")


# ==================== 管理接口（Basic Auth） ====================

@app.get("/api/admin/entries", response_model=List[DiaryEntry], tags=["管理接口（需登录）"])
async def admin_get_entries(
    query: Optional[str] = Query(None, description="搜索关键词"),
    date_from: Optional[str] = Query(None, description="起始日期"),
    date_to: Optional[str] = Query(None, description="结束日期"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    username: str = Depends(verify_admin_credentials)
):
    """
    管理端查询日记（需要登录）
    
    使用HTTP Basic Auth认证
    """
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Build query
        query_parts = ["SELECT * FROM diaries WHERE 1=1"]
        params = []
        
        if query:
            query_parts.append("AND content LIKE ?")
            params.append(f"%{query}%")
        
        if date_from:
            query_parts.append("AND date >= ?")
            params.append(date_from)
        
        if date_to:
            query_parts.append("AND date <= ?")
            params.append(date_to)
        
        query_parts.append("ORDER BY date DESC, id DESC")
        query_parts.append(f"LIMIT {limit} OFFSET {offset}")
        
        final_query = " ".join(query_parts)
        cursor.execute(final_query, params)
        
        entries = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@app.get("/api/admin/entries/{entry_id}", response_model=DiaryEntry, tags=["管理接口（需登录）"])
async def admin_get_entry(
    entry_id: int,
    username: str = Depends(verify_admin_credentials)
):
    """获取单条日记详情（需要登录）"""
    entry = db.get_entry_by_id(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="日记不存在")
    return entry


@app.put("/api/admin/entries/{entry_id}", response_model=DiaryEntry, tags=["管理接口（需登录）"])
async def admin_update_entry(
    entry_id: int,
    update_data: DiaryUpdate,
    username: str = Depends(verify_admin_credentials)
):
    """
    更新日记条目（需要登录）
    
    可以更新日期和内容
    """
    # Check if entry exists
    entry = db.get_entry_by_id(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="日记不存在")
    
    # Update
    success = db.update_entry(
        entry_id,
        date=update_data.date,
        content=update_data.content
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="更新失败，可能是重复条目")
    
    # Return updated entry
    updated_entry = db.get_entry_by_id(entry_id)
    return updated_entry


@app.delete("/api/admin/entries/{entry_id}", tags=["管理接口（需登录）"])
async def admin_delete_entry(
    entry_id: int,
    username: str = Depends(verify_admin_credentials)
):
    """删除日记条目（需要登录）"""
    success = db.delete_entry(entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="日记不存在")
    
    return {"message": f"日记 {entry_id} 已删除"}


@app.get("/api/admin/stats", tags=["管理接口（需登录）"])
async def admin_get_stats(username: str = Depends(verify_admin_credentials)):
    """获取管理端统计信息（需要登录）"""
    try:
        stats = db.get_statistics()
        
        # Add some admin-specific stats
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Recent entries (last 7 days)
        cursor.execute("""
            SELECT date, COUNT(*) as count 
            FROM diaries 
            WHERE date >= date('now', '-7 days')
            GROUP BY date 
            ORDER BY date DESC
        """)
        recent_activity = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        stats["recent_activity"] = recent_activity
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


# ==================== 启动服务 ====================

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("菜根日记存档 API 服务")
    print("=" * 60)
    print(f"服务地址: http://0.0.0.0:{PORT}")
    print(f"API文档: http://0.0.0.0:{PORT}/docs")
    print(f"ReDoc文档: http://0.0.0.0:{PORT}/redoc")
    print("=" * 60)
    print(f"管理员用户名: {ADMIN_USERNAME}")
    print(f"API Key: {API_KEY[:10]}...")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )

