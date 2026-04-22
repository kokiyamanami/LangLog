import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { ErrorBoundary } from './components/ErrorBoundary'
import { ProtectedRoute } from './components/ProtectedRoute'
import { LandingPage } from './pages/LandingPage'
import { LoginPage } from './pages/LoginPage'
import { DashboardPage } from './pages/DashboardPage'
import { MyPage } from './pages/MyPage'
import { CalendarPage } from './pages/CalendarPage'
import { NotFoundPage } from './pages/NotFoundPage'

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        {/* AuthProvider：全子コンポーネントに認証コンテキストを提供 */}
        <AuthProvider>
          <Routes>
            {/* ランディングページ：ルート（/）のルート */}
            <Route path="/" element={<LandingPage />} />
            
            {/* ログインページ：/login のルート */}
            <Route path="/login" element={<LoginPage />} />
            
            {/* ダッシュボード：/dashboard のルート（ProtectedRoute でラップして認証確認） */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />

            {/* カレンダー：/calendar のルート（ProtectedRoute でラップして認証確認） */}
            <Route
              path="/calendar"
              element={
                <ProtectedRoute>
                  <CalendarPage />
                </ProtectedRoute>
              }
            />

            {/* マイページ：/mypage のルート（ProtectedRoute でラップして認証確認） */}
            <Route
              path="/mypage"
              element={
                <ProtectedRoute>
                  <MyPage />
                </ProtectedRoute>
              }
            />

            {/* 404 Not Found：定義されていないすべてのルート */}
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </ErrorBoundary>
  )
}

export default App
