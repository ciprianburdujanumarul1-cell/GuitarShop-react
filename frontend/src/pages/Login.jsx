import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [code, setCode] = useState('')
  const [needs2FA, setNeeds2FA] = useState(false)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      const res = await login(email, password, needs2FA ? code : undefined)

      if (res?.requires_2fa) {
        setNeeds2FA(true)
        setSubmitting(false)
        return
      }

      const dest = location.state?.from?.pathname || '/'
      navigate(dest, { replace: true })
    } catch {
      setError(needs2FA ? 'Cod 2FA incorect.' : 'Email or password incorrect')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-wrap">
      <h1 className="auth-title">Log<span>in</span></h1>

      {error && <div className="alert alert-error">{error}</div>}

      <form onSubmit={handleSubmit}>
        {!needs2FA && (
          <>
            <div className="form-field">
              <label htmlFor="email">Email</label>
              <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            </div>
            <div className="form-field">
              <label htmlFor="password">Password</label>
              <input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            </div>
          </>
        )}

        {needs2FA && (
          <div className="form-field">
            <label htmlFor="code">Cod din Authenticator</label>
            <input
              id="code"
              type="text"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              maxLength={6}
              autoFocus
              required
            />
          </div>
        )}

        <button className="btn-block" type="submit" disabled={submitting}>
          {submitting ? 'Signing in…' : needs2FA ? 'Confirmă codul' : 'Login'}
        </button>
      </form>

      {!needs2FA && (
        <p className="auth-switch">
          Don't have an account? <Link to="/signin">Sign up</Link>
        </p>
      )}
    </div>
  )
}