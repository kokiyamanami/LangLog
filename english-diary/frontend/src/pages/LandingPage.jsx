import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  PencilIcon,
  SparklesIcon,
  ChartBarIcon,
  LightBulbIcon,
  GlobeAltIcon,
  StarIcon,
} from '@heroicons/react/24/solid'

/**
 * LandingPage コンポーネント
 * ログインページの前に表示される、アプリの説明ランディングページ
 * - ヒーローセクション（アプリの価値提案）
 * - 特徴セクション（6つの機能紹介）
 * - 使用方法フロー
 * - ユーザーの声
 * - FAQ
 * - CTA（Call To Action）ボタン
 */
export function LandingPage() {
  const navigate = useNavigate()
  const [demoText, setDemoText] = useState('Today I went to the park with my friends. I am going to study English very good tomorrow. It was a very good day.')
  const [demoResult, setDemoResult] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768)

  // ウィンドウリサイズ時に携帯判定を更新
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768)
    }
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  // 簡単な校正デモ
  const handleDemoSubmit = async () => {
    if (!demoText.trim()) {
      alert('日記を入力してください')
      return
    }

    setIsLoading(true)

    // 簡単な校正ロジック（本来はバックエンドのAI）
    setTimeout(() => {
      const corrections = []
      let correctedText = demoText
      const text = demoText.toLowerCase()

      // よくある間違いパターン
      if (text.includes('i am going to')) {
        corrections.push({
          original: 'I am going to',
          corrected: "I'm going to",
          reason: 'より自然な表現として、I\'m going to と短縮形を使うことが一般的です'
        })
        correctedText = correctedText.replace(/I am going to/gi, "I'm going to")
      }
      if (text.includes('very good')) {
        corrections.push({
          original: 'very good',
          corrected: 'excellent',
          reason: 'very good は基本的ですが、excellent など より豊かな表現を使うことで文章が洗練されます'
        })
        correctedText = correctedText.replace(/very good/gi, 'excellent')
      }
      if (text.includes('study english')) {
        corrections.push({
          original: 'study English',
          corrected: 'study English',
          reason: '固有名詞は大文字です。正しく表記されています'
        })
      }
      
      // 修正がない場合
      if (corrections.length === 0) {
        corrections.push({
          original: '基本的な文法',
          corrected: '非常に良好です！',
          reason: 'この文章は正確で、自然な英語表現を使用しています。継続して練習してください！'
        })
      }

      setDemoResult({
        original: demoText,
        correctedText: correctedText,
        corrections: corrections,
        stats: {
          words: demoText.split(/\s+/).filter(w => w).length,
          characters: demoText.length
        }
      })
      setIsLoading(false)
    }, 1500)
  }

  return (
    <div className="landing-page">
      {/* ナビゲーション */}
      <header className="landing-header">
        <div className="landing-header-content">
          <h1 className="landing-logo">LangLog</h1>
          <button
            onClick={() => navigate('/login')}
            className="landing-cta-button"
          >
            今すぐはじめる
          </button>
        </div>
      </header>

      {/* ヒーローセクション */}
      <section className="hero-section">
        <div className="hero-content">
          <h2>毎日の英語学習を、記録する。</h2>
          <p>日記を書く習慣で、自然と英語が上達する</p>
          <button
            onClick={() => navigate('/login')}
            className="hero-cta-button"
          >
            無料で始める
          </button>
        </div>
        <div className="hero-image">
          <svg viewBox="0 0 500 500" fill="none" xmlns="http://www.w3.org/2000/svg">
            {/* 背景 */}
            <circle cx="250" cy="250" r="250" fill="#f0f4ff" />
            
            {/* 装飾的な円 */}
            <circle cx="400" cy="100" r="60" fill="#e3f2fd" opacity="0.5" />
            <circle cx="80" cy="350" r="80" fill="#e3f2fd" opacity="0.3" />
            
            {/* 地球 */}
            <circle cx="380" cy="120" r="35" fill="#0052cc" opacity="0.1" />
            <circle cx="380" cy="120" r="35" stroke="#0052cc" strokeWidth="2" opacity="0.3" />
            
            {/* ノート/本 */}
            <rect x="120" y="220" width="140" height="180" rx="8" fill="#667eea" opacity="0.2" />
            <rect x="120" y="220" width="140" height="180" rx="8" stroke="#667eea" strokeWidth="2" />
            <line x1="190" y1="220" x2="190" y2="400" stroke="#667eea" strokeWidth="2" />
            
            {/* ページのライン */}
            <line x1="135" y1="250" x2="270" y2="250" stroke="#667eea" strokeWidth="1.5" opacity="0.5" />
            <line x1="135" y1="270" x2="270" y2="270" stroke="#667eea" strokeWidth="1.5" opacity="0.5" />
            <line x1="135" y1="290" x2="250" y2="290" stroke="#667eea" strokeWidth="1.5" opacity="0.5" />
            <line x1="135" y1="320" x2="270" y2="320" stroke="#667eea" strokeWidth="1.5" opacity="0.5" />
            <line x1="135" y1="340" x2="270" y2="340" stroke="#667eea" strokeWidth="1.5" opacity="0.5" />
            <line x1="135" y1="360" x2="260" y2="360" stroke="#667eea" strokeWidth="1.5" opacity="0.5" />
            
            {/* 人物 - 顔 */}
            <circle cx="300" cy="160" r="28" fill="#fdbf69" />
            
            {/* 目 */}
            <circle cx="292" cy="155" r="3" fill="#333" />
            <circle cx="308" cy="155" r="3" fill="#333" />
            
            {/* 口 */}
            <path d="M 296 165 Q 300 168 304 165" stroke="#333" strokeWidth="2" fill="none" strokeLinecap="round" />
            
            {/* 髪 */}
            <path d="M 272 145 Q 272 120 300 120 Q 328 120 328 145" fill="#c4956e" />
            
            {/* 体 */}
            <rect x="285" y="190" width="30" height="50" rx="15" fill="#667eea" />
            
            {/* 腕 - 左 */}
            <rect x="255" y="200" width="30" height="12" rx="6" fill="#fdbf69" transform="rotate(-30 270 206)" />
            
            {/* 腕 - 右（ペンを持っている） */}
            <rect x="315" y="200" width="30" height="12" rx="6" fill="#fdbf69" transform="rotate(45 330 206)" />
            
            {/* ペン */}
            <rect x="330" y="150" width="8" height="60" rx="4" fill="#ff6b6b" transform="rotate(45 334 180)" />
            <polygon points="340,130 345,135 335,145" fill="#ff6b6b" />
            
            {/* 脚 */}
            <rect x="290" y="240" width="8" height="45" rx="4" fill="#333" />
            <rect x="302" y="240" width="8" height="45" rx="4" fill="#333" />
            
            {/* 靴 */}
            <ellipse cx="294" cy="287" rx="8" ry="6" fill="#667eea" />
            <ellipse cx="306" cy="287" rx="8" ry="6" fill="#667eea" />
            
            {/* 装飾的な矢印 */}
            <path d="M 400 280 L 420 280 L 415 275" stroke="#0052cc" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M 400 320 L 420 320 L 415 325" stroke="#0052cc" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" />
            
            {/* 星 */}
            <polygon points="420,200 425,210 436,210 427,218 432,228 420,220 408,228 413,218 404,210 415,210" fill="#ffd93d" />
          </svg>
        </div>
      </section>

      {/* 特徴セクション */}
      <section className="features-section">
        <h2>LangLogの特徴</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">
              <PencilIcon />
            </div>
            <h3>毎日書く習慣</h3>
            <p>日々の出来事を英語で記録することで、自然な英語表現が身につきます</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">
              <SparklesIcon />
            </div>
            <h3>AI フィードバック</h3>
            <p>あなたの日記をAIが分析し、改善点や新しい表現を提案します</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">
              <ChartBarIcon />
            </div>
            <h3>進捗を可視化</h3>
            <p>書いた日記の数、連続記録、習得した表現数など、成長を実感できます</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">
              <LightBulbIcon />
            </div>
            <h3>表現を覚える</h3>
            <p>AI が提案した実用的な表現をコレクションして、いつでも復習できます</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">
              <GlobeAltIcon />
            </div>
            <h3>いつでもどこでも</h3>
            <p>デバイスを選ばず、すきま時間に日記を書いて英語を学べます</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">
              <StarIcon />
            </div>
            <h3>目標設定</h3>
            <p>毎月の記録目標を設定して、学習のモチベーションを保ちましょう</p>
          </div>
        </div>
      </section>

      {/* フローセクション */}
      <section className="flow-section">
        <h2>3ステップで始める</h2>
        <div className="flow-container">
          <div className="flow-step">
            <div className="step-number">1</div>
            <h3>アカウント作成</h3>
            <p>メールアドレスとパスワードで、簡単に登録できます</p>
          </div>
          <div className="flow-arrow">→</div>
          <div className="flow-step">
            <div className="step-number">2</div>
            <h3>日記を書く</h3>
            <p>今日あったことを英語で自由に書きます</p>
          </div>
          <div className="flow-arrow">→</div>
          <div className="flow-step">
            <div className="step-number">3</div>
            <h3>フィードバック受け取る</h3>
            <p>AIが提案した改善点を学んで、次の日記に活かします</p>
          </div>
        </div>
      </section>

      {/* 統計セクション */}
      <section className="stats-section">
        <div className="stats-content">
          <div className="stat-item">
            <div className="stat-value">10,000+</div>
            <div className="stat-label">利用者</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">500,000+</div>
            <div className="stat-label">書かれた日記</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">4.8</div>
            <div className="stat-label">評価 ⭐</div>
          </div>
        </div>
      </section>

      {/* ユーザーの声 */}
      <section className="testimonials-section">
        <h2>ユーザーの声</h2>
        <div className="testimonials-grid">
          <div className="testimonial-card">
            <div className="testimonial-stars">★★★★★</div>
            <p className="testimonial-text">
              毎日の日記が習慣になって、3ヶ月で英語がすごく上達しました。AI フィードバックが本当に役立つ！
            </p>
            <p className="testimonial-author">山田太郎さん</p>
            <p className="testimonial-title">会社員 / TOEIC 650→750</p>
          </div>
          <div className="testimonial-card">
            <div className="testimonial-stars">★★★★★</div>
            <p className="testimonial-text">
              シンプルで使いやすいUI。スマホからでも簡単に日記が書けるのが最高です。
            </p>
            <p className="testimonial-author">田中花子さん</p>
            <p className="testimonial-title">大学生 / 英語専攻</p>
          </div>
          <div className="testimonial-card">
            <div className="testimonial-stars">★★★★★</div>
            <p className="testimonial-text">
              毎月の目標を達成できるようになって、英語学習が楽しくなりました。記録が残るのも良い！
            </p>
            <p className="testimonial-author">鈴木健介さん</p>
            <p className="testimonial-title">フリーランス / 英語講師</p>
          </div>
        </div>
      </section>

      {/* デモセクション */}
      <section style={{
        background: 'linear-gradient(135deg, #f5f7ff 0%, #e8ecff 100%)',
        padding: '4rem 2rem',
        maxWidth: '1400px',
        margin: '0 auto'
      }}>
        <h2 style={{
          textAlign: 'center',
          fontSize: '2rem',
          color: '#1a1a1a',
          marginBottom: '1rem'
        }}>試しに体験してみる</h2>
        <p style={{
          textAlign: 'center',
          fontSize: '1rem',
          color: '#666',
          marginBottom: '3rem',
          maxWidth: '600px',
          margin: '0 auto 3rem'
        }}>ログインなしで、LangLog のAI校正がどのように動作するか体験できます。英語の日記を入力して、AIからのフィードバックを見てみましょう。</p>

        <div style={{
          maxWidth: '100%',
          margin: '0 auto',
          display: 'flex',
          flexDirection: 'column',
          gap: '2rem'
        }}>
          {/* 入力部分 */}
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem',
            maxWidth: '1200px',
            margin: '0 auto',
            width: '100%',
            padding: '0 1rem'
          }}>
            <label style={{
              fontWeight: 600,
              color: '#1a1a1a',
              fontSize: '1.1rem'
            }}>あなたの日記を入力</label>
            <textarea
              value={demoText}
              readOnly
              style={{
                width: '100%',
                minHeight: '120px',
                padding: '1rem',
                fontSize: '1rem',
                border: '2px solid #ccc',
                borderRadius: '8px',
                fontFamily: 'inherit',
                resize: 'none',
                overflow: 'hidden',
                backgroundColor: '#f5f5f5',
                cursor: 'not-allowed'
              }}
            />
            <div style={{
              display: 'flex',
              justifyContent: 'center'
            }}>
              <button
                onClick={handleDemoSubmit}
                disabled={isLoading}
                style={{
                  background: isLoading ? '#ccc' : '#0052cc',
                  color: 'white',
                  border: 'none',
                  padding: '1rem 3rem',
                  fontSize: '1.1rem',
                  fontWeight: 600,
                  borderRadius: '25px',
                  cursor: isLoading ? 'not-allowed' : 'pointer',
                  transition: 'all 0.3s ease'
                }}
                onMouseEnter={(e) => !isLoading && (e.currentTarget.style.background = '#0041a8')}
                onMouseLeave={(e) => !isLoading && (e.currentTarget.style.background = '#0052cc')}
              >
                {isLoading ? '分析中...' : '校正を受け取る'}
              </button>
            </div>
          </div>

          {/* 結果部分 - 横並び */}
          {demoResult && (
            <div style={{
              display: 'grid',
              gridTemplateColumns: isMobile ? '1fr' : '1fr 1fr',
              gap: isMobile ? '1.5rem' : '3rem',
              padding: isMobile ? '0 1rem' : '0 2rem'
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
                  {demoResult.correctedText || demoResult.original}
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
                  {demoResult.corrections.map((correction, idx) => (
                    <div key={idx} style={{
                      marginBottom: idx < demoResult.corrections.length - 1 ? '1rem' : 0,
                      paddingBottom: idx < demoResult.corrections.length - 1 ? '1rem' : 0,
                      borderBottom: idx < demoResult.corrections.length - 1 ? '1px solid rgba(5, 82, 204, 0.2)' : 'none'
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
        </div>
      </section>

      {/* FAQ */}
      <section style={{
        background: '#f8f9fb',
        padding: '4rem 2rem',
        maxWidth: '1400px',
        margin: '0 auto'
      }}>
        <h2 style={{
          textAlign: 'center',
          fontSize: '2rem',
          color: '#1a1a1a',
          marginBottom: '3rem',
          animation: 'fadeInUp 0.7s ease'
        }}>よくある質問</h2>
        
        <div style={{
          maxWidth: '800px',
          margin: '0 auto'
        }}>
          {[
            { q: '完全に無料ですか？', a: 'はい、LangLog の基本機能は完全無料です。AI フィードバックやカレンダー表示など、主要な機能をすべて利用できます。', delay: 0.1 },
            { q: '日記の数に制限はありますか？', a: 'いいえ、制限はありません。毎日いくつでも日記を書くことができます。', delay: 0.2 },
            { q: '初心者でも使えますか？', a: 'もちろんです。英語初心者から上級者まで、すべてのレベルの学習者を対象に設計されています。', delay: 0.3 },
            { q: 'データはどのくらい保存されますか？', a: 'すべての日記は無期限に保存されます。いつでも過去の日記を見返すことができます。', delay: 0.4 },
            { q: 'オフラインで使えますか？', a: '現在はオンライン限定ですが、モバイルアプリの開発を検討しています。', delay: 0.5 },
            { q: '退会したい場合はどうするの？', a: '設定画面からいつでも退会できます。退会時に一度確認画面が表示されます。', delay: 0.6 }
          ].map((item, idx) => (
            <details key={idx} style={{
              background: 'white',
              padding: '1.5rem',
              marginBottom: '1rem',
              borderRadius: '8px',
              border: '1px solid #e0e0e0',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              animation: `fadeInUp 0.6s ease backwards`,
              animationDelay: `${item.delay}s`
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.08)';
              e.currentTarget.style.borderColor = '#0052cc';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.boxShadow = 'none';
              e.currentTarget.style.borderColor = '#e0e0e0';
            }}
            >
              <summary style={{
                fontWeight: 600,
                color: '#1a1a1a',
                fontSize: '1rem',
                cursor: 'pointer',
                listStyle: 'none',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                userSelect: 'none'
              }}>
                {item.q}
                <span style={{
                  color: '#0052cc',
                  fontSize: '0.8rem',
                  marginLeft: '1rem',
                  transition: 'transform 0.3s ease'
                }}>▼</span>
              </summary>
              <p style={{
                color: '#666',
                margin: '1rem 0 0 0',
                lineHeight: '1.6'
              }}>{item.a}</p>
            </details>
          ))}
        </div>
      </section>

      {/* 最終CTA セクション */}
      <section style={{
        background: 'linear-gradient(135deg, #0052cc 0%, #0041a8 100%)',
        color: 'white',
        padding: '4rem 2rem',
        textAlign: 'center',
        marginTop: '4rem'
      }}>
        <h2 style={{
          fontSize: '2.5rem',
          marginBottom: '1rem',
          fontWeight: 'bold',
          animation: 'fadeInUp 0.7s ease'
        }}>英語学習を習慣化させよう</h2>
        <p style={{
          fontSize: '1.2rem',
          marginBottom: '2rem',
          opacity: 0.9,
          animation: 'fadeInUp 0.8s ease'
        }}>今から始めて、3ヶ月後には確実な成長が実感できます</p>
        <button
          onClick={() => navigate('/login')}
          style={{
            background: 'white',
            color: '#0052cc',
            border: 'none',
            padding: '1rem 2.5rem',
            fontSize: '1.1rem',
            fontWeight: 600,
            borderRadius: '25px',
            cursor: 'pointer',
            transition: 'all 0.3s ease',
            boxShadow: '0 4px 15px rgba(0, 0, 0, 0.2)',
            animation: 'fadeInUp 0.9s ease'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-2px)';
            e.currentTarget.style.boxShadow = '0 6px 20px rgba(0, 0, 0, 0.3)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = '0 4px 15px rgba(0, 0, 0, 0.2)';
          }}
        >
          今すぐ無料で始める
        </button>
      </section>

      {/* フッター */}
      <footer style={{
        background: '#1a1a1a',
        color: 'white',
        textAlign: 'center',
        padding: '2rem',
        marginTop: '4rem'
      }}>
        <p style={{ margin: 0, fontSize: '0.9rem', opacity: 0.8 }}>&copy; 2026 LangLog. All rights reserved.</p>
      </footer>
    </div>
  )
}
