from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate, PasswordChange
from app.services.auth_service import verify_token, get_user_by_id
from passlib.context import CryptContext

# パスワードハッシング設定：bcryptアルゴリズムを使用
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/api/v1/users", tags=["users"])


def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    認証ヘッダーからBearerトークンを取得して検証し、現在のユーザーを返す
    
    ヘッダー形式：Authorization: Bearer <token>
    
    Args:
        authorization: Authorization ヘッダーの値
        db: データベースセッション
    
    Returns:
        User: トークンに対応するユーザーオブジェクト
    
    Raises:
        HTTPException: ヘッダーが無い、形式が不正、トークンが無効な場合
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    
    token = parts[1]
    user_id = verify_token(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """
    現在のユーザープロフィール情報を取得
    
    ログイン中のユーザーの全プロフィール情報をJSON形式で返す。
    
    Returns:
        UserResponse: ユーザーのプロフィール情報（パスワードハッシュは除外）
    """
    return UserResponse.model_validate(current_user)


@router.put("/profile", response_model=UserResponse)
def update_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ユーザープロフィール情報を更新
    
    名前や性別などのプロフィール情報を更新する。
    更新後、DBに保存して更新後のプロフィール全体を返す。
    
    Args:
        user_data: 更新するプロフィール情報
        current_user: 現在のユーザー（依存性注入で自動取得）
        db: データベースセッション
    
    Returns:
        UserResponse: 更新後のプロフィール情報
    """
    if user_data.name:
        current_user.name = user_data.name
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)


@router.post("/change-password", status_code=200)
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ユーザーのパスワードを変更
    
    現在のパスワードを確認してから、新しいパスワードに更新。
    パスワード確認フィールドでの値の一致、長さ検証なども行う。
    
    Args:
        password_data: 現在のパスワードと新しいパスワード
        current_user: 現在のユーザー（依存性注入で自動取得）
        db: データベースセッション
    
    Returns:
        dict: 成功メッセージ
    """
    # 現在のパスワードが正しいか確認
    if not pwd_context.verify(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    # 新しいパスワードが一致しているか確認
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match"
        )
    
    # パスワードの長さを確認
    if len(password_data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    
    # パスワードをハッシュして更新
    current_user.hashed_password = pwd_context.hash(password_data.new_password)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return {"message": "Password changed successfully"}
