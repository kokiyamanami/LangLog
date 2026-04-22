from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.database import Base


class Diary(Base):
    """日記エントリモデル"""
    __tablename__ = "diaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    original_text = Column(Text, nullable=False)
    corrected_text = Column(Text, nullable=True)
    corrections = Column(JSON, nullable=True)  # 校正内容の配列を保存
    stats = Column(JSON, nullable=True)  # 文字数、単語数などの統計情報
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーションシップ
    user = relationship("User", backref="diaries")

    def __repr__(self):
        return f"<Diary(id={self.id}, user_id={self.user_id}, created_at={self.created_at})>"
