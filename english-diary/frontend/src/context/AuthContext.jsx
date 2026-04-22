import { createContext, useState, useEffect } from 'react'
import { authAPI, userAPI } from '../services/api'

// 認証コンテキスト：ユーザーの認証状態を管理
export const AuthContext = createContext()

/**
 * AuthProvider コンポーネント
 * ユーザーの認証状態をアプリケーション全体で管理
 * 
 * 提供する値：
 * - user: 現在のユーザー情報（認証済みの場合）
 * - loading: 初期認証チェック中かどうか
 * - register: 新規登録メソッド
 * - login: ログインメソッド
 * - logout: ログアウトメソッド
 * - updateUserProfile: プロフィール更新メソッド
 */
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // マウント時：ローカルストレージのトークンから既存ユーザーをチェック
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('access_token')
        const refreshToken = localStorage.getItem('refresh_token')
        
        // トークンが両方存在する場合のみ認証チェック
        if (token && refreshToken) {
          try {
            // トークンが有効な場合、ユーザー情報を取得
            const { data } = await authAPI.me()
            setUser(data)
          } catch (error) {
            // トークンが無効な場合、ローカルストレージから削除
            console.error('Auth token validation failed:', error)
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            setUser(null)
          }
        } else if (token || refreshToken) {
          // どちらか片方だけある場合は不整合なので両方削除
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          setUser(null)
        }
        // トークンがない場合は user = null のまま
      } finally {
        setLoading(false)
      }
    }

    checkAuth()
  }, [])

  /**
   * 新規登録メソッド
   * @param {string} name - ユーザーの名前
   * @param {string} email - メールアドレス
   * @param {string} password - パスワード
   */
  const register = async (name, email, password) => {
    // バックエンド API に登録リクエスト送信
    const { data } = await authAPI.register({ name, email, password })
    // アクセストークン と リフレッシュトークンをローカルストレージに保存
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    // ユーザー状態を更新
    setUser(data.user)
    return data
  }

  /**
   * ログインメソッド
   * @param {string} email - メールアドレス
   * @param {string} password - パスワード
   */
  const login = async (email, password) => {
    // バックエンド API にログインリクエスト送信
    const { data } = await authAPI.login({ email, password })
    // アクセストークン と リフレッシュトークンをローカルストレージに保存
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    // ユーザー状態を更新
    setUser(data.user)
    return data
  }

  /**
   * ログアウトメソッド
   * ローカルストレージのトークンを削除してユーザー状態をクリア
   */
  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
  }

  /**
   * プロフィール更新メソッド
   * @param {object} profileData - 更新するプロフィール情報
   */
  const updateUserProfile = async (profileData) => {
    const { data } = await userAPI.updateProfile(profileData)
    setUser(data)
    return data
  }

  // コンテキスト値を子コンポーネントに提供
  return (
    <AuthContext.Provider value={{ user, loading, register, login, logout, updateUserProfile }}>
      {children}
    </AuthContext.Provider>
  )
}

