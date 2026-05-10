import { useState } from 'react'
import {
  EyeIcon,
  EyeSlashIcon,
} from '@heroicons/react/24/solid'

/**
 * AuthForm コンポーネント
 * ログインと新規登録用の共有フォーム
 * - ニックネーム入力（新規登録時のみ）
 * - メールアドレス入力
 * - パスワード入力（表示/非表示切り替え機能付き）
 * - エラーメッセージ表示
 * - フォーム送信
 */
export function AuthForm({ isRegister = false, onSubmit, loading = false }) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')

  // フォーム送信時の処理
  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    try {
      if (isRegister) {
        // 新規登録の場合：名前、メール、パスワードを送信
        await onSubmit(name, email, password)
      } else {
        // ログインの場合：メール、パスワードを送信
        await onSubmit(email, password)
      }
    } catch (err) {
      // エラーメッセージをサーバーレスポンスから取得
      const detail = err.response?.data?.detail
      if (detail === 'Email already registered') {
        setError('このメールアドレスはすでに登録されています')
      } else if (detail === 'Invalid credentials') {
        setError('メールアドレスまたはパスワードが正しくありません')
      } else if (Array.isArray(detail)) {
        setError(detail.map(d => d.msg).join(', '))
      } else {
        setError(detail || 'エラーが発生しました')
      }
    }
  }

  return (
    <form onSubmit={handleSubmit} className="auth-form">
      {/* 新規登録モード時のみ：ニックネーム入力フィールドを表示 */}
      {isRegister && (
        <div className="form-group">
          <label htmlFor="name">ニックネーム</label>
          <input
            type="text"
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            maxLength="100"
          />
        </div>
      )}

      {/* メールアドレス入力フィールド（必須） */}
      <div className="form-group">
        <label htmlFor="email">メールアドレス</label>
        <input
          type="email"
          id="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>

      {/* パスワード入力フィールド：表示/非表示切り替え機能付き */}
      <div className="form-group">
        <label htmlFor="password">パスワード</label>
        <div className="password-input-group">
          {/* showPassword状態によってinput typeを切り替え（password/text） */}
          <input
            type={showPassword ? 'text' : 'password'}
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength="8"
            maxLength="72"
          />
          {/* パスワード表示/非表示切り替えボタン：Heroiconsアイコン使用 */}
          <button
            type="button"
            className="password-toggle-button"
            onClick={() => setShowPassword(!showPassword)}
            title={showPassword ? '非表示' : '表示'}
          >
            {/* showPassword状態によってアイコンを切り替え（EyeIcon/EyeSlashIcon） */}
            {showPassword ? (
              <EyeSlashIcon className="password-icon" />
            ) : (
              <EyeIcon className="password-icon" />
            )}
          </button>
        </div>
      </div>

      {/* エラーメッセージ表示：エラーが存在する場合のみ表示 */}
      {error && <div className="error-message">{error}</div>}

      {/* フォーム送信ボタン：loading状態中は無効化 */}
      <button type="submit" disabled={loading} className="submit-button">
        {/* loading状態によってボタンテキストを切り替え */}
        {loading ? '処理中...' : isRegister ? '登録' : 'ログイン'}
      </button>
    </form>
  )
}
