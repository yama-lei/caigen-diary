"""
Pydantic models for the diary API.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class DiaryEntry(BaseModel):
    """日记条目"""
    id: int
    date: str
    content: str
    created_at: str


class DiaryCreate(BaseModel):
    """创建日记条目"""
    date: str = Field(..., description="日期 (YYYY-MM-DD)")
    content: str = Field(..., min_length=1, description="日记内容")


class DiaryUpdate(BaseModel):
    """更新日记条目"""
    date: Optional[str] = Field(None, description="日期 (YYYY-MM-DD)")
    content: Optional[str] = Field(None, min_length=1, description="日记内容")


class BatchCreateRequest(BaseModel):
    """批量创建日记请求"""
    entries: List[DiaryCreate] = Field(..., description="日记列表")


class BatchCreateResponse(BaseModel):
    """批量创建日记响应"""
    total: int = Field(..., description="总条数")
    success: int = Field(..., description="成功添加条数")
    duplicate: int = Field(..., description="重复条数")
    failed: int = Field(..., description="失败条数")
    details: List[dict] = Field(default_factory=list, description="详细信息")


class Statistics(BaseModel):
    """统计信息"""
    total: int
    date_range: dict
    monthly_counts: dict

