from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List


class CorrectionItem(BaseModel):
    """校正アイテム"""
    original: str
    corrected: str
    reason: str


class CorrectionStats(BaseModel):
    """校正統計情報"""
    words: int
    characters: int


class DiaryCreate(BaseModel):
    """日記作成スキーマ"""
    original_text: str = Field(..., min_length=1, description="元のテキスト")


class DiaryResponse(BaseModel):
    """日記レスポンススキーマ"""
    id: UUID
    user_id: UUID
    original_text: str
    corrected_text: Optional[str] = None
    corrections: Optional[List[CorrectionItem]] = None
    stats: Optional[CorrectionStats] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
