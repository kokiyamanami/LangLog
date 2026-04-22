import { useContext, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AuthContext } from '../context/AuthContext'
import { AuthForm } from '../components/AuthForm'

/**
 * LoginPage コンポーネント
 * ユーザーのログイン・新規登録を行うページ
 * - 新規登録フォーム / ログインフォーム の切り替え機能
 * - 認証エラー時のエラーメッセージ表示
 * - 成功時は /dashboard にリダイレクト
 */
export function LoginPage() {
  const { login, register } = useContext(AuthContext)
  const navigate = useNavigate()
  const [isRegister, setIsRegister] = useState(false)
  const [loading, setLoading] = useState(false)

  // ログイン処理
  const handleLogin = async (email, password) => {
    setLoading(true)
    try {
      await login(email, password)
      navigate('/dashboard')
    } finally {
      setLoading(false)
    }
  }

  // 新規登録処理
  const handleRegister = async (name, email, password) => {
    setLoading(true)
    try {
      await register(name, email, password)
      navigate('/dashboard')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-container">
        <h1>{isRegister ? '新規登録' : 'ログイン'}</h1>

        <AuthForm
          isRegister={isRegister}
          onSubmit={isRegister ? handleRegister : handleLogin}
          loading={loading}
        />

        <div className="toggle-section">
          <span>{isRegister ? 'すでにアカウントをお持ちですか？' : 'アカウントをお持ちでないですか？'}</span>
          <button
            type="button"
            onClick={() => setIsRegister(!isRegister)}
            className="toggle-button"
          >
            {isRegister ? 'ログイン' : '登録'}
          </button>
        </div>
      </div>
    </div>
  )
}
