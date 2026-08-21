import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

export const api = axios.create({
  baseURL: `${API_URL}/api`,
})

function getTokens() {
  return {
    access: localStorage.getItem('access'),
    refresh: localStorage.getItem('refresh'),
  }
}

export function setTokens({ access, refresh }) {
  if (access) localStorage.setItem('access', access)
  if (refresh) localStorage.setItem('refresh', refresh)
}

export function clearTokens() {
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
}

// Attach the access token to every request.
api.interceptors.request.use((config) => {
  const { access } = getTokens()
  if (access) {
    config.headers.Authorization = `Bearer ${access}`
  }
  return config
})

// On a 401, try to refresh the access token once and replay the request.
let refreshingPromise = null

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      const { refresh } = getTokens()
      if (!refresh) {
        clearTokens()
        return Promise.reject(error)
      }

      try {
        if (!refreshingPromise) {
          refreshingPromise = axios
            .post(`${API_URL}/api/auth/refresh/`, { refresh })
            .finally(() => {
              refreshingPromise = null
            })
        }
        const { data } = await refreshingPromise
        setTokens({ access: data.access })
        original.headers.Authorization = `Bearer ${data.access}`
        return api(original)
      } catch (refreshError) {
        clearTokens()
        return Promise.reject(refreshError)
      }
    }
    return Promise.reject(error)
  }
)

export default api
