import { useContext, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AuthContext } from '../context/AuthContext'
import { userAPI } from '../services/api'
import {
  UserCircleIcon,
  EnvelopeIcon,
  LockClosedIcon,
  ArrowLeftIcon,
} from '@heroicons/react/24/solid'

/**
 * MyPage コンポーネント
 * ユーザープロフィール情報の表示と編集
 * 
 * 機能：
 * - プロフィール情報表示（名前、メールアドレス）
 * - プロフィール編集
 * - パスワード変更
 * - ログアウト
 * - ダッシュボードへ戻る
 */
export function MyPage() {
  const navigate = useNavigate()
  const { user, logout, updateUserProfile } = useContext(AuthContext)

  const [isEditing, setIsEditing] = useState(false)
  const [name, setName] = useState(user?.name || '')
  const [showPasswordChange, setShowPasswordChange] = useState(false)
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  // プロフィール編集を保存
  const handleSaveProfile = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setIsLoading(true)

    try {
      // バックエンド API でプロフィール更新
      await updateUserProfile({ name })
      setIsEditing(false)
      setSuccess('プロフィールが更新されました')
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(err.response?.data?.detail || 'プロフィール更新に失敗しました')
    } finally {
      setIsLoading(false)
    }
  }

  // パスワード変更を処理
  const handleChangePassword = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    // バリデーション
    if (newPassword !== confirmPassword) {
      setError('新しいパスワードが一致しません')
      return
    }

    if (newPassword.length < 8) {
      setError('パスワードは 8 文字以上である必要があります')
      return
    }

    setIsLoading(true)

    try {
      // バックエンド API でパスワード変更
      await userAPI.changePassword({
        current_password: currentPassword,
        new_password: newPassword
      })
      setShowPasswordChange(false)
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
      setSuccess('パスワードが変更されました')
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(err.response?.data?.detail || 'パスワード変更に失敗しました')
    } finally {
      setIsLoading(false)
    }
  }

  // ログアウト処理
  const handleLogout = () => {
    logout()
    navigate('/')
  }

  // ダッシュボードに戻る
  const handleBack = () => {
    navigate('/dashboard')
  }

  return (
    <div className="mypage">
      {/* ナビゲーションバー */}
      <header className="mypage-header">
        <div className="mypage-header-content">
          <button className="back-button" onClick={handleBack} title="戻る">
            <ArrowLeftIcon className="icon-small" />
            <span>戻る</span>
          </button>
          <h1 className="mypage-title">マイページ</h1>
          <div style={{ width: '60px' }}></div>
        </div>
      </header>

      {/* メインコンテンツ */}
      <main className="mypage-content">
        <div className="mypage-container">
          {/* メッセージ表示 */}
          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message">{success}</div>}

          {/* プロフィールセクション */}
          <section className="profile-section">
            <div className="section-header">
              <UserCircleIcon className="section-icon" />
              <h2>プロフィール情報</h2>
            </div>

            {!isEditing ? (
              <div className="profile-view">
                {/* 名前表示 */}
                <div className="profile-field">
                  <label>ニックネーム</label>
                  <p>{name}</p>
                </div>

                {/* メールアドレス表示 */}
                <div className="profile-field">
                  <label>メールアドレス</label>
                  <p>{user?.email}</p>
                </div>

                {/* 編集ボタン */}
                <button
                  className="primary-button"
                  onClick={() => setIsEditing(true)}
                >
                  編集
                </button>
              </div>
            ) : (
              <form onSubmit={handleSaveProfile} className="profile-edit-form">
                {/* ニックネーム編集 */}
                <div className="form-group">
                  <label htmlFor="name">ニックネーム</label>
                  <input
                    id="name"
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="太郎"
                    required
                  />
                </div>

                {/* メールアドレス（読み取り専用） */}
                <div className="form-group">
                  <label htmlFor="email">メールアドレス</label>
                  <input
                    id="email"
                    type="email"
                    value={user?.email}
                    disabled
                    className="input-disabled"
                  />
                  <small>メールアドレスはサポートに連絡して変更してください</small>
                </div>

                {/* ボタングループ */}
                <div className="button-group">
                  <button 
                    type="submit" 
                    className="primary-button"
                    disabled={isLoading}
                  >
                    {isLoading ? '保存中...' : '保存'}
                  </button>
                  <button
                    type="button"
                    className="secondary-button"
                    onClick={() => setIsEditing(false)}
                    disabled={isLoading}
                  >
                    キャンセル
                  </button>
                </div>
              </form>
            )}
          </section>

          {/* セキュリティセクション */}
          <section className="security-section">
            <div className="section-header">
              <LockClosedIcon className="section-icon" />
              <h2>セキュリティ</h2>
            </div>

            {!showPasswordChange ? (
              <div className="security-view">
                <p className="security-description">
                  アカウントのセキュリティを確保するため、定期的にパスワードを変更してください
                </p>
                <button
                  className="primary-button"
                  onClick={() => setShowPasswordChange(true)}
                >
                  パスワードを変更
                </button>
              </div>
            ) : (
              <form
                onSubmit={handleChangePassword}
                className="password-change-form"
              >
                {/* 現在のパスワード */}
                <div className="form-group">
                  <label htmlFor="current-password">現在のパスワード</label>
                  <input
                    id="current-password"
                    type="password"
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                  />
                </div>

                {/* 新しいパスワード */}
                <div className="form-group">
                  <label htmlFor="new-password">新しいパスワード</label>
                  <input
                    id="new-password"
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="••••••••"
                    minLength="8"
                    required
                  />
                  <small>8 文字以上である必要があります</small>
                </div>

                {/* パスワード確認 */}
                <div className="form-group">
                  <label htmlFor="confirm-password">パスワード確認</label>
                  <input
                    id="confirm-password"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                  />
                </div>

                {/* ボタングループ */}
                <div className="button-group">
                  <button 
                    type="submit" 
                    className="primary-button"
                    disabled={isLoading}
                  >
                    {isLoading ? '変更中...' : '変更'}
                  </button>
                  <button
                    type="button"
                    className="secondary-button"
                    onClick={() => {
                      setShowPasswordChange(false)
                      setCurrentPassword('')
                      setNewPassword('')
                      setConfirmPassword('')
                      setError('')
                    }}
                    disabled={isLoading}
                  >
                    キャンセル
                  </button>
                </div>
              </form>
            )}
          </section>

          {/* アカウントセクション */}
          <section className="account-section">
            <div className="section-header">
              <EnvelopeIcon className="section-icon" />
              <h2>アカウント</h2>
            </div>

            <div className="account-actions">
              <button className="danger-button" onClick={handleLogout}>
                ログアウト
              </button>
            </div>
          </section>
        </div>
      </main>
    </div>
  )
}
