import { useContext, useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { AuthContext } from '../context/AuthContext'
import { diaryAPI } from '../services/api'
import {
  PencilIcon,
  SparklesIcon,
  LightBulbIcon,
  UserCircleIcon,
  ArrowRightIcon,
} from '@heroicons/react/24/solid'

/**
 * DashboardPage コンポーネント
 * ログイン後のメイン画面
 * 以下の要素で構成：
 * - ナビゲーションバー（ロゴ、ユーザー名、マイページボタン）
 * - ウェルカムセクション（日記作成のCTA）
 * - 日記作成モーダル（テキストエリア）
 * - 統計情報（日記数、連続記録、改善単語数）
 * - 最近の日記一覧
 * - 学習のコツ（3つのカード）
 */
export function DashboardPage() {
  const { user } = useContext(AuthContext)
  const navigate = useNavigate()
  const [content, setContent] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [recentDiaries, setRecentDiaries] = useState([])
  const [diaryStats, setDiaryStats] = useState({
    monthlyCount: 0,
    consecutiveDays: 0,
    improvedWords: 0
  })
  const [isLoadingDiaries, setIsLoadingDiaries] = useState(false)

  /**
   * 最近の日記を取得する関数
   * マウント時と日記保存後に呼ばれて、DBから日記一覧を取得し、
   * 統計情報を再計算する。APIは最新10件を返す。
   */
  const fetchRecentDiaries = async () => {
    setIsLoadingDiaries(true)
    try {
      const response = await diaryAPI.listDiaries(0, 10)
      setRecentDiaries(response.data || [])
      
      // 統計情報を計算
      calculateStats(response.data || [])
    } catch (err) {
      console.error('日記の取得に失敗しました：', err)
    } finally {
      setIsLoadingDiaries(false)
    }
  }

  /**
   * 統計情報を計算する関数
   * APIから取得した日記データから、以下の統計を計算：
   * - monthlyCount: 今月保存した日記の数
   * - consecutiveDays: 連続して日記を書いた日数（簡易版）
   * - improvedWords: 全日記の校正件数合計（改善されたフレーズ数）
   * 
   * @param {Array} diaries - APIから取得した日記配列
   */
  const calculateStats = (diaries) => {
    if (!diaries || diaries.length === 0) {
      setDiaryStats({
        monthlyCount: 0,
        consecutiveDays: 0,
        improvedWords: 0
      })
      return
    }

    const now = new Date()
    const currentMonth = now.getMonth()
    const currentYear = now.getFullYear()

    // 今月の日記数を計算
    const monthlyDiaries = diaries.filter(diary => {
      const diaryDate = new Date(diary.created_at)
      return diaryDate.getMonth() === currentMonth && diaryDate.getFullYear() === currentYear
    })

    // 改善された単語数を計算
    let improvedCount = 0
    diaries.forEach(diary => {
      if (diary.corrections) {
        improvedCount += diary.corrections.length
      }
    })

    setDiaryStats({
      monthlyCount: monthlyDiaries.length,
      consecutiveDays: Math.min(diaries.length, 7), // 簡易版：最大7日
      improvedWords: improvedCount
    })
  }

  useEffect(() => {
    fetchRecentDiaries()
  }, [])

  // マイページへナビゲート
  const handleGoToMyPage = () => {
    navigate('/mypage')
  }

  /**
   * 日記送信処理：実際のテキストをAPIに送信して校正
   * - 入力値をバリデーション
   * - APIに POST リクエストを送信
   * - 校正結果を state に保存してUI表示
   * - 完了後、日記リストを再取得して統計更新
   */
  const handleSubmitDiary = async () => {
    if (!content.trim()) {
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      // APIに日記を送信
      const response = await diaryAPI.createDiary({
        original_text: content
      })

      // APIレスポンスから結果を設定
      setResult({
        original: response.data.original_text,
        correctedText: response.data.corrected_text,
        corrections: response.data.corrections,
        stats: response.data.stats
      })

      // 入力をクリア
      setContent('')

      // 最近の日記を再取得
      setTimeout(() => {
        fetchRecentDiaries()
      }, 500)
    } catch (err) {
      console.error('日記の保存に失敗しました：', err)
      setError(err.response?.data?.detail || '日記の保存に失敗しました')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="dashboard-page">
      {/* ナビゲーションバー */}
      <header className="dashboard-header">
        <div className="header-content">
          <h1 className="logo">LangLog</h1>
          <div className="header-actions">
            <span className="user-name">{user?.name}さん</span>
            <button
              onClick={handleGoToMyPage}
              className="mypage-button"
              title="マイページ"
            >
              <UserCircleIcon className="icon-button" />
            </button>
          </div>
        </div>
      </header>

      {/* Google翻訳スタイルのナビゲーション */}
      <div className="nav-switcher">
        <button 
          className="nav-button current"
          disabled
        >
          <span className="nav-label">日記</span>
        </button>
        <button 
          className="nav-button"
          onClick={() => navigate('/calendar')}
          title="カレンダーに移動"
        >
          <span className="nav-label">カレンダー</span>
        </button>
      </div>

      {/* メインコンテンツ */}
      <main className="dashboard-content">
        {/* 日記作成セクション */}
        <section className="diary-input-section">
          <div className="diary-input-container">
            <h2>あなたの日記を入力</h2>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="今日の出来事や学習内容を英語で書いてください..."
              className="diary-textarea"
              rows="8"
            />
            <div className="diary-actions">
              <button
                onClick={handleSubmitDiary}
                className="primary-button"
                disabled={!content.trim() || isLoading}
              >
                {isLoading ? '保存中...' : '保存 & AI判定'}
              </button>
            </div>
          </div>

          {/* 結果部分 - 横並び */}
          {result && (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'isMobile ? 1fr : 1fr 1fr',
              gap: '3rem',
              padding: '2rem 0',
              maxWidth: '1000px',
              margin: '0 auto'
            }}>
              {/* 校正済みの英語 */}
              <div>
                <label style={{
                  fontWeight: 600,
                  color: '#1a1a1a',
                  fontSize: '1.1rem',
                  display: 'block',
                  marginBottom: '0.5rem'
                }}>校正済みの英語</label>
                <div style={{
                  background: '#d4edda',
                  padding: '1.5rem',
                  borderRadius: '8px',
                  border: '2px solid #28a745',
                  fontSize: '1rem',
                  color: '#155724',
                  lineHeight: '1.8',
                  minHeight: '150px',
                  fontStyle: 'italic'
                }}>
                  {result.correctedText || result.original}
                </div>
              </div>

              {/* 校正理由 */}
              <div>
                <label style={{
                  fontWeight: 600,
                  color: '#1a1a1a',
                  fontSize: '1.1rem',
                  display: 'block',
                  marginBottom: '0.5rem'
                }}>校正理由</label>
                <div style={{
                  background: '#e3f2fd',
                  padding: '1.5rem',
                  borderRadius: '8px',
                  border: '2px solid #0052cc',
                  borderLeft: '4px solid #0052cc',
                  fontSize: '0.95rem',
                  color: '#1565c0',
                  lineHeight: '1.8',
                  minHeight: '350px'
                }}>
                  {result.corrections.map((correction, idx) => (
                    <div key={idx} style={{
                      marginBottom: idx < result.corrections.length - 1 ? '1rem' : 0,
                      paddingBottom: idx < result.corrections.length - 1 ? '1rem' : 0,
                      borderBottom: idx < result.corrections.length - 1 ? '1px solid rgba(5, 82, 204, 0.2)' : 'none'
                    }}>
                      <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>
                        💡 {correction.original}
                      </div>
                      <div style={{ fontSize: '0.9rem', opacity: 0.9 }}>
                        {correction.reason}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </section>

        {/* 統計情報 */}
        <section className="stats-section">
          <div className="stat-card">
            <div className="stat-number">{diaryStats.monthlyCount}</div>
            <div className="stat-label">今月の日記数</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{diaryStats.consecutiveDays}</div>
            <div className="stat-label">連続記録日数</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{diaryStats.improvedWords}</div>
            <div className="stat-label">改善された単語</div>
          </div>
        </section>

        {/* 学習のコツ */}
        <section className="tips-section">
          <h3>LangLog の効果的な使い方</h3>
          <div className="tips-grid">
            <div className="tip-card">
              <div className="tip-icon">
                <PencilIcon className="heroicon" />
              </div>
              <h4>毎日書く</h4>
              <p>
                毎日の習慣にすることで、英語表現が自然に身につきます。
              </p>
            </div>
            <div className="tip-card">
              <div className="tip-icon">
                <SparklesIcon className="heroicon" />
              </div>
              <h4>AIフィードバック</h4>
              <p>
                文法や表現の改善提案を受けて、着実に上達します。
              </p>
            </div>
            <div className="tip-card">
              <div className="tip-icon">
                <LightBulbIcon className="heroicon" />
              </div>
              <h4>表現を覚える</h4>
              <p>
                フィードバックから学んだ表現を、次の日記に活かします。
              </p>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}
