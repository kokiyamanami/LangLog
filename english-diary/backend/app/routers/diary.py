from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
import re

from app.database import get_db
from app.models.diary import Diary
from app.schemas.diary import DiaryCreate, DiaryResponse, CorrectionItem, CorrectionStats
from app.routers.users import get_current_user
from app.models.user import User


router = APIRouter(
    prefix="/api/v1/diary",
    tags=["diary"]
)


def mock_correct_text(text: str) -> tuple[str, list]:
    """
    モック校正関数：パターンマッチングを使った簡易的な英文校正
    
    実際のAI実装（AWS、OpenAI等）の代わりに使用するモック校正機能。
    複数のパターンマッチングルールを適用してテキストを修正し、
    修正内容と修正理由をリストで返す。
    
    Returns:
        tuple: (修正されたテキスト, 修正内容のリスト)
        例: ("I'm going to...", [{"original": "I am", "corrected": "I'm", "reason": "..."}])
    
    Note:
        実装当初はパターンベースだが、将来的には以下に置き換え可能：
        - Claude API（Anthropic）
        - OpenAI GPT-4
        - AWS Comprehend
    """
    corrections = []
    corrected = text

    # パターンベースの校正ルール
    patterns = [
        # 短縮形の提案
        (r'\bI am\b', 'I\'m', 'I am を I\'m に短縮（カジュアルな表現）'),
        (r'\bI am going to\b', 'I\'m going to', 'I am going to を短縮形に（日常会話）'),
        (r'\byou are\b', 'you\'re', 'you are を you\'re に短縮'),
        (r'\bhe is\b', 'he\'s', 'he is を he\'s に短縮'),
        (r'\bshe is\b', 'she\'s', 'she is を she\'s に短縮'),
        
        # 時制の提案
        (r'\bI go\b', 'I went', '過去形に修正：go → went（過去の出来事の場合）'),
        (r'\bI see\b', 'I saw', '過去形に修正：see → saw'),
        
        # 文法的な修正
        (r'\bvery good\b', 'excellent', 'より自然な表現に：very good → excellent'),
        (r'\bvery bad\b', 'terrible', 'より自然な表現に：very bad → terrible'),
        (r'\bI like very much\b', 'I like it very much', '目的語の追加：it が必要'),
        
        # スペルチェック
        (r'\brecieve\b', 'receive', 'スペルミス修正：recieve → receive'),
        (r'\boccured\b', 'occurred', 'スペルミス修正：occured → occurred'),
    ]

    for original_pattern, corrected_word, reason in patterns:
        # 大文字小文字を区別しないマッチングを行う
        matches = list(re.finditer(original_pattern, corrected, re.IGNORECASE))
        
        if matches:
            # 最後のマッチから処理（インデックスズレを防ぐため逆順）
            for match in reversed(matches):
                # 元のテキストから該当部分を取得
                original_match = match.group(0)
                
                # 大文字小文字を保持する
                if original_match[0].isupper():
                    corrected_match = corrected_word[0].upper() + corrected_word[1:]
                else:
                    corrected_match = corrected_word.lower()
                
                # 校正内容を記録
                corrections.append({
                    "original": original_match,
                    "corrected": corrected_match,
                    "reason": reason
                })
                
                # テキストを置換
                corrected = corrected[:match.start()] + corrected_match + corrected[match.end():]

    return corrected, corrections


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
        # モック校正を実行
        corrected_text, corrections = mock_correct_text(diary_data.original_text)
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
