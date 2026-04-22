import { useContext, useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { SimpleCalendar } from './SimpleCalendar'
import { AuthContext } from '../context/AuthContext'
import { diaryAPI } from '../services/api'
import { UserCircleIcon, XMarkIcon, ArrowRightIcon } from '@heroicons/react/24/solid'
import './CalendarPage.css'

/**
 * CalendarPage コンポーネント
 * 月表示カレンダーで日記の記録日を表示
 * 日付をクリックするとその日の日記一覧をモーダルで表示
 */
export function CalendarPage() {
  const { user } = useContext(AuthContext)
  const navigate = useNavigate()
  const [allDiaries, setAllDiaries] = useState([])
  const [selectedDate, setSelectedDate] = useState(new Date())
  const [selectedDateDiaries, setSelectedDateDiaries] = useState([])
  const [showModal, setShowModal] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  /**
   * コンポーネントマウント時：全日記データを取得
   * カレンダーに表示する日記データ（最大100件）をAPIから取得
   * 以降の日付クリック時にこのデータを検索して表示
   */
  useEffect(() => {
    fetchAllDiaries()
  }, [])

  /**
   * 全日記データをAPIから取得する関数
   * リスト最大100件をメモリに保持し、以降の日付マッチングに使用。
   * パフォーマンス最適化のため、一度の読み込みで全月データを取得。
   */
  const fetchAllDiaries = async () => {
    setIsLoading(true)
    try {
      const response = await diaryAPI.listDiaries(0, 100) // 最大100件取得
      setAllDiaries(response.data || [])
    } catch (err) {
      console.error('日記の取得に失敗しました：', err)
    } finally {
      setIsLoading(false)
    }
  }

  /**
   * 日付をYYYY-MM-DD形式の文字列に変換
   */
  const formatDateToString = (date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }

  /**
   * 特定の日付の日記を取得するヘルパー関数
   * 日付文字列（YYYY-MM-DD）でマッチングして、その日の日記を絞り込む。
   * 
   * @param {Date} date - 検索対象の日付
   * @returns {Array} その日付の日記配列
   */
  const getDiariesForDate = (date) => {
    const targetDateStr = formatDateToString(date)
    return allDiaries.filter(diary => {
      const diaryDateStr = formatDateToString(new Date(diary.created_at))
      return diaryDateStr === targetDateStr
    })
  }

  /**
   * 日付をクリックしたときの処理
   * モーダルを開いて、その日の日記詳細を表示
   */
  const handleDateClick = (date) => {
    setSelectedDate(date)
    const diaries = getDiariesForDate(date)
    setSelectedDateDiaries(diaries)
    setShowModal(true)
  }

  /**
   * react-calendarのタイルコンテンツをカスタマイズする関数
   * 日記がある日付に青いドット（●）と日記数を表示。
   * 
   * @param {Date} date - タイルの日付
   * @returns {JSX|null} 表示するコンテンツ（日記がない場合はnull）
   */
  const getTileContent = (date) => {
    const diaries = getDiariesForDate(date)
    if (diaries.length > 0) {
      return (
        <div className="calendar-tile-content">
          <div className="calendar-dot"></div>
          <div className="calendar-count">{diaries.length}</div>
        </div>
      )
    }
    return null
  }

  /**
   * react-calendarのタイルクラスをカスタマイズする関数
   * 日記がある日付に特殊なクラス名を付与して、CSSで青くハイライト表示。
   * 
   * @param {Object} param - react-calendarから渡される日付オブジェクト
   * @returns {string} 適用するクラス名（例：'diary-date'）
   */
  const getTileClassName = ({ date }) => {
    const diaries = getDiariesForDate(date)
    if (diaries.length > 0) {
      return 'diary-date'
    }
    return ''
  }

  // マイページへナビゲート
  const handleGoToMyPage = () => {
    navigate('/mypage')
  }

  return (
    <div className="calendar-page">
      {/* ナビゲーションバー */}
      <header className="calendar-header">
        <div className="header-content">
          <h1 className="logo" onClick={() => navigate('/dashboard')} style={{ cursor: 'pointer' }}>
            LangLog
          </h1>
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
          className="nav-button"
          onClick={() => navigate('/dashboard')}
          title="ダッシュボードに戻る"
        >
          <span className="nav-label">日記</span>
        </button>
        <button 
          className="nav-button current"
          disabled
        >
          <span className="nav-label">カレンダー</span>
        </button>
      </div>

      {/* メインコンテンツ */}
      <main className="calendar-content">
        <div className="calendar-container">
          <div className="calendar-wrapper">
            <h2>日記カレンダー</h2>
            <p className="calendar-subtitle">
              青色でハイライトされた日は日記を書いた日です。日付をクリックすると詳細が表示されます。
            </p>

            {isLoading ? (
              <div className="loading-state">
                <p>読み込み中...</p>
              </div>
            ) : (
              <SimpleCalendar
                value={selectedDate}
                onClickDay={handleDateClick}
                tileContent={getTileContent}
                tileClassName={getTileClassName}
              />
            )}

            <div className="calendar-stats">
              <div className="stat">
                <span className="stat-label">総日記数</span>
                <span className="stat-value">{allDiaries.length}</span>
              </div>
              <div className="stat">
                <span className="stat-label">記録日数</span>
                <span className="stat-value">
                  {new Set(allDiaries.map(d => formatDateToString(new Date(d.created_at)))).size}
                </span>
              </div>
              <div className="stat">
                <span className="stat-label">総校正件数</span>
                <span className="stat-value">
                  {allDiaries.reduce((sum, d) => sum + (d.corrections?.length || 0), 0)}
                </span>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* モーダル */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>
                {selectedDate.toLocaleDateString('ja-JP', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                  weekday: 'long'
                })}
                の日記
              </h3>
              <button
                className="close-button"
                onClick={() => setShowModal(false)}
                title="閉じる"
              >
                <XMarkIcon className="close-icon" />
              </button>
            </div>

            <div className="modal-body">
              {selectedDateDiaries.length === 0 ? (
                <div className="empty-state">
                  <p>この日の日記はありません</p>
                </div>
              ) : (
                <div className="diary-list">
                  {selectedDateDiaries.map((diary) => (
                    <div key={diary.id} className="diary-card">
                      <div className="diary-card-header">
                        <h4>
                          {new Date(diary.created_at).toLocaleTimeString('ja-JP', {
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                          に保存
                        </h4>
                        <span className="diary-corrections">
                          校正: {diary.corrections?.length || 0}件
                        </span>
                      </div>
                      <div className="diary-card-content">
                        <div className="original-text">
                          <label>元のテキスト</label>
                          <p>{diary.original_text}</p>
                        </div>
                        {diary.corrected_text && (
                          <div className="corrected-text">
                            <label>校正済みテキスト</label>
                            <p>{diary.corrected_text}</p>
                          </div>
                        )}
                        {diary.corrections && diary.corrections.length > 0 && (
                          <div className="corrections-list">
                            <label>校正理由</label>
                            {diary.corrections.map((correction, idx) => (
                              <div key={idx} className="correction-item">
                                <div className="correction-original">
                                  💡 {correction.original}
                                </div>
                                <div className="correction-reason">
                                  {correction.reason}
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
