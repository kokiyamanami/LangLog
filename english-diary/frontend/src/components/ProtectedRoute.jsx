import { useContext } from 'react'
import { Navigate } from 'react-router-dom'
import { AuthContext } from '../context/AuthContext'

/**
 * ProtectedRoute コンポーネント
 * 認証が必要なページへのアクセスを保護する
 * 
 * 動作：
 * - ローディング中：読み込み中メッセージを表示
 * - 認証済み（user存在）：子コンポーネントを表示
 * - 未認証（user未設定）：ランディングページ（/）へリダイレクト
 * 
 * ポイント：
 * - リロード時に loading が完了するまで待機
 * - loading が false になるまでリダイレクトしない
 */
export function ProtectedRoute({ children }) {
  const { user, loading } = useContext(AuthContext)

  // ローディング完了を待つまでは読み込み中を表示
  // これによりリロード時のトークン検証が完了するまで待機
  if (loading) {
    return (
      <div style={{ 
        padding: '20px', 
        textAlign: 'center',
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#fafbff',
        fontFamily: 'system-ui, -apple-system, sans-serif'
      }}>
        <div>
          <div style={{ fontSize: '1.2rem', color: '#0052cc', fontWeight: '600' }}>読み込み中...</div>
          <div style={{ fontSize: '0.9rem', color: '#999', marginTop: '0.5rem' }}>認証情報を確認しています</div>
        </div>
      </div>
    )
  }

  // ローディング完了後、ユーザーが認証済みなら子コンポーネントを表示
  // そうでなければランディングページへリダイレクト
  return user ? children : <Navigate to="/" replace />
}
