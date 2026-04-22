import React from 'react'
import './ErrorBoundary.css'

/**
 * ErrorBoundary - React エラーバウンダリー
 * 子コンポーネント内で発生したエラーをキャッチして表示
 */
export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true }
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
    this.setState({
      error: error,
      errorInfo: errorInfo,
    })
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    })
    // ページをリロード
    window.location.href = '/'
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <div className="error-container">
            {/* エラーアイコン */}
            <div className="error-icon">⚠️</div>

            {/* エラータイトル */}
            <h1 className="error-title">予期しないエラーが発生しました</h1>
            
            {/* エラーメッセージ */}
            <p className="error-description">
              申し訳ありません。アプリケーションに問題が発生しました。
              ページをリロードするか、ホームに戻ってください。
            </p>

            {/* 開発環境：エラー詳細を表示 */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="error-details">
                <summary>技術詳細（開発用）</summary>
                <div className="error-message">
                  <strong>エラーメッセージ:</strong>
                  <pre>{this.state.error.toString()}</pre>
                </div>
                {this.state.errorInfo && (
                  <div className="error-stack">
                    <strong>スタックトレース:</strong>
                    <pre>{this.state.errorInfo.componentStack}</pre>
                  </div>
                )}
              </details>
            )}

            {/* アクション */}
            <div className="error-actions">
              <button 
                className="error-button error-primary"
                onClick={this.handleReset}
              >
                ホームに戻る
              </button>
              <button 
                className="error-button error-secondary"
                onClick={() => window.location.reload()}
              >
                ページをリロード
              </button>
            </div>

            {/* サポート情報 */}
            <p className="error-support">
              問題が解決しない場合は、サポートまでお問い合わせください。
            </p>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
