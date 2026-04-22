import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'

// グローバルスタイル
import './index.css'
import './App.css'

// ページスタイル
import './pages/LandingPage.css'
import './pages/LoginPage.css'
import './pages/DashboardPage.css'
import './pages/MyPage.css'

// コンポーネントスタイル
import './components/AuthForm.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
