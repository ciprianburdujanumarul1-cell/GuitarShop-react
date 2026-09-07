import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import api, { setTokens, clearTokens } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const loadMe = useCallback(async () => {
    const access = localStorage.getItem('access')
    if (!access) {
      setLoading(false)
      return
    }
    try {
      const { data } = await api.get('/auth/me/')
      setUser(data)
    } catch {
      clearTokens()
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadMe()
  }, [loadMe])

  async function login(email, password, code) {
    try {
      const { data } = await api.post('/auth/login/', { email, password, code })
      setTokens({ access: data.access, refresh: data.refresh })
      setUser(data.user)
      return data.user
    } catch (err) {
      console.log('LOGIN ERROR:', err.response?.status, err.response?.data)
      const errData = err.response?.data
      const requires2FA = Array.isArray(errData?.requires_2fa)
        ? errData.requires_2fa[0]
        : errData?.requires_2fa

      if (requires2FA) {
        return { requires_2fa: true }
      }
      throw err
    }
  }

  async function register(payload) {
    await api.post('/auth/register/', payload)
  }

  function logout() {
    clearTokens()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}