from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
import re
import json
import logging
from openai import OpenAI

from app.database import get_db
from app.models.diary import Diary
from app.schemas.diary import DiaryCreate, DiaryResponse, CorrectionItem, CorrectionStats
from app.routers.users import get_current_user
from app.models.user import User
from app.config import settings

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/api/v1/diary",
    tags=["diary"]
)


def ai_correct_text(text: str) -> tuple[str, list]:
    """
    OpenAI GPT-4o-mini を使った英文AI添削

    Returns:
        tuple: (添削後テキスト, 修正内容のリスト)
    """
    if not settings.OPENAI_API_KEY:
        # APIキー未設定時はフォールバック（空の添削）
        logger.warning("OPENAI_API_KEY が設定されていません。添削をスキップします。")
        return text, []

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    system_prompt = """You are an expert English writing coach specializing in helping Japanese learners improve their English diary entries.

Your task is to proofread the given English text and return corrections in JSON format.

Rules:
- Correct grammar errors, spelling mistakes, and unnatural expressions
- Suggest more natural English phrasing when appropriate
- Keep the original meaning and tone
- If the text is already correct, return an empty corrections array

Return ONLY valid JSON in this exact format:
{
  "corrected_text": "<full corrected text>",
  "corrections": [
    {
      "original": "<original phrase>",
      "corrected": "<corrected phrase>",
      "reason": "<explanation in Japanese>"
    }
  ]
}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Please proofread this English diary entry:\n\n{text}"}
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
        max_tokens=1000,
    )

    result = json.loads(response.choices[0].message.content)
    corrected_text = result.get("corrected_text", text)
    corrections = result.get("corrections", [])

    return corrected_text, corrections


def calculate_stats(text: str) -> dict:
    """テキストの統計情報を計算
    
    与えられたテキストの単語数と文字数をカウントして返す。
    ユーザーの学習進度を視覚化するために使用される。
    
    Args:
        text: 統計を計算する英文テキスト
    
    Returns:
        dict: {"words": 単語数, "characters": 文字数}
    """
    words = len(text.split())
    characters = len(text)
    return {
        "words": words,
        "characters": characters
    }


@router.post("/", response_model=DiaryResponse, status_code=status.HTTP_201_CREATED)
async def create_diary(
    diary_data: DiaryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    日記を作成・保存し、モック校正結果を返す
    
    Args:
        diary_data: 日記のテキストデータ
        current_user: 現在ログインしているユーザー
        db: データベースセッション
    
    Returns:
        DiaryResponse: 日記データと校正結果
    """
    try:
        # AI添削を実行
        corrected_text, corrections = ai_correct_text(diary_data.original_text)
        stats = calculate_stats(diary_data.original_text)

        # データベースに保存
        diary = Diary(
            user_id=current_user.id,
            original_text=diary_data.original_text,
            corrected_text=corrected_text,
            corrections=corrections,
            stats=stats
        )
        
        db.add(diary)
        db.commit()
        db.refresh(diary)

        return diary

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"日記の保存に失敗しました: {str(e)}"
        )


@router.get("/{diary_id}", response_model=DiaryResponse)
async def get_diary(
    diary_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    特定の日記を取得
    """
    diary = db.query(Diary).filter(
        Diary.id == diary_id,
        Diary.user_id == current_user.id
    ).first()

    if not diary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日記が見つかりません"
        )

    return diary


@router.get("/", response_model=list[DiaryResponse])
async def list_diaries(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = 20
):
    """
    ユーザーの日記一覧を取得（新しい順）
    """
    diaries = db.query(Diary).filter(
        Diary.user_id == current_user.id
    ).order_by(Diary.created_at.desc()).offset(skip).limit(limit).all()

    return diaries
