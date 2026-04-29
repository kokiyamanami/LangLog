import axios from 'axios'

/**
 * APIクライアント設定モジュール
 * 
 * このモジュールはaxiosインスタンスを設定し、全APIリクエストに対して：
 * - JWT トークンの自動付与
 * - トークン有効期限切れ時の自動更新
 * - エラーハンドリング
 * を実装している。
 */

const API_URL = process.env.REACT_APP_API_URL || import.meta.env.VITE_API_URL || 'http://3.112.58.39:8000/api/v1'

// Axiosインスタンスを作成（全APIリクエストに使用）
const apiClient = axios.create({
  baseURL: API_URL,
})

/**
 * リクエストインターセプター：全リクエストに認証トークンを自動付与
 * ローカルストレージに保存されたJWTトークンをAuthorizationヘッダーに追加
 */
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

/**
 * レスポンスインターセプター：トークン有効期限切れ時の自動更新
 * 
 * 401エラーが返ってきた場合、refresh_tokenを使って新しいaccess_tokenを取得
 * その後、元のリクエストを再実行してユーザー体験を向上させる。
 * 
 * refresh_tokenも無効な場合はレジェクトを返す（ProtectedRoute でハンドル）
 */
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const { data } = await axios.post(`${API_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          })
          localStorage.setItem('access_token', data.access_token)
          originalRequest.headers.Authorization = `Bearer ${data.access_token}`
          return apiClient(originalRequest)
        } catch (refreshError) {
          // リフレッシュも失敗した場合はトークンをクリア
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          // リダイレクトしない：AuthContext の checkAuth で null になるのを待つ
          return Promise.reject(refreshError)
        }
      } else {
        // refresh_token がない場合もトークンをクリア
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        return Promise.reject(error)
      }
    }

    return Promise.reject(error)
  }
)


/**
 * 認証APIエンドポイント
 * ログイン、登録、トークン更新、ユーザー情報取得
 */
export const authAPI = {
  register: (data) => apiClient.post('/auth/register', data),
  login: (data) => apiClient.post('/auth/login', data),
  refresh: (refreshToken) => apiClient.post('/auth/refresh', { refresh_token: refreshToken }),
  me: () => apiClient.get('/auth/me'),
}

/**
 * ユーザープロフィール管理APIエンドポイント
 * プロフィール取得・更新、パスワード変更
 */
export const userAPI = {
  getProfile: () => apiClient.get('/users/profile'),
  updateProfile: (data) => apiClient.put('/users/profile', data),
  changePassword: (data) => apiClient.post('/users/change-password', data),
}

/**
 * 日記管理APIエンドポイント
 * 日記の作成、取得、一覧表示（校正結果含む）
 */
export const diaryAPI = {
  createDiary: (data) => apiClient.post('/diary/', data),
  getDiary: (id) => apiClient.get(`/diary/${id}`),
  listDiaries: (skip = 0, limit = 20) => apiClient.get('/diary/', { params: { skip, limit } }),
}

export default apiClient
