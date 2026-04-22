import { useNavigate } from 'react-router-dom'
import './NotFoundPage.css'

/**
 * NotFoundPage - 404 エラーページ
 * 存在しないルートにアクセスした場合に表示
 */
export function NotFoundPage() {
  const navigate = useNavigate()

  return (
    <div className="not-found-page">
      <div className="not-found-container">
        {/* エラーコード */}
        <div className="not-found-code">404</div>

        {/* エラーメッセージ */}
        <h1 className="not-found-title">ページが見つかりません</h1>
        <p className="not-found-description">
          申し訳ありません。お探しのページは存在しないか、移動された可能性があります。
        </p>

        {/* アクション */}
        <div className="not-found-actions">
          <button 
            className="not-found-button not-found-primary"
            onClick={() => navigate('/')}
          >
            ホームに戻る
          </button>
          <button 
            className="not-found-button not-found-secondary"
            onClick={() => navigate(-1)}
          >
            前のページに戻る
          </button>
        </div>

        {/* デコレーション */}
        <div className="not-found-icon">?</div>
      </div>
    </div>
  )
}
