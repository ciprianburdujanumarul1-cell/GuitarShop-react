import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const initialForm = {
  username: '',
  email: '',
  password: '',
  country: '',
  city: '',
  address: '',
  postal_code: '',
}

export default function Signup() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState(initialForm)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  function update(field) {
    return (e) => setForm((prev) => ({ ...prev, [field]: e.target.value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await register(form)
      navigate('/login', { replace: true })
    } catch (err) {
      const data = err.response?.data
      const firstError = data && Object.values(data)[0]
      setError(Array.isArray(firstError) ? firstError[0] : firstError || 'A apărut o eroare la înregistrare.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-wrap">
      <h1 className="auth-title">Sign<span>up</span></h1>

      {error && <div className="alert alert-error">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-field">
          <label htmlFor="username">Username</label>
          <input id="username" value={form.username} onChange={update('username')} required />
        </div>
        <div className="form-field">
          <label htmlFor="email">Email</label>
          <input id="email" type="email" value={form.email} onChange={update('email')} required />
        </div>
        <div className="form-field">
          <label htmlFor="password">Password</label>
          <input id="password" type="password" value={form.password} onChange={update('password')} required />
        </div>
        <div className="form-row-2">
          <div className="form-field">
            <label htmlFor="country">Country</label>
            <input id="country" value={form.country} onChange={update('country')} required />
          </div>
          <div className="form-field">
            <label htmlFor="city">City</label>
            <input id="city" value={form.city} onChange={update('city')} required />
          </div>
        </div>
        <div className="form-row-2">
          <div className="form-field">
            <label htmlFor="address">Address</label>
            <input id="address" value={form.address} onChange={update('address')} required />
          </div>
          <div className="form-field">
            <label htmlFor="postal_code">Postal code</label>
            <input id="postal_code" value={form.postal_code} onChange={update('postal_code')} required />
          </div>
        </div>
        <button className="btn-block" type="submit" disabled={submitting}>
          {submitting ? 'Creating account…' : 'Sign up'}
        </button>
      </form>

      <p className="auth-switch">
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </div>
  )
}
