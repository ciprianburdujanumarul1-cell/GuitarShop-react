import { useState, useEffect } from 'react'
import api from '../api/client'

export default function TwoFactorSetup() {
  const [checking, setChecking] = useState(true)
  const [isEnabled, setIsEnabled] = useState(false)
  const [qrCode, setQrCode] = useState(null)
  const [secret, setSecret] = useState('')
  const [code, setCode] = useState('')
  const [status, setStatus] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    async function checkStatus() {
      try {
        const { data } = await api.get('/auth/2fa/status/')
        setIsEnabled(data.is_enabled)
      } catch {
        setStatus('Nu am putut verifica starea 2FA.')
      } finally {
        setChecking(false)
      }
    }
    checkStatus()
  }, [])

  async function startSetup() {
    setLoading(true)
    setStatus('')
    try {
      const { data } = await api.post('/auth/2fa/setup/')
      setQrCode(data.qr_code)
      setSecret(data.secret)
    } catch (err) {
      setStatus(err.response?.data?.detail || 'Eroare la generarea codului QR.')
    } finally {
      setLoading(false)
    }
  }

  async function confirmCode(e) {
    e.preventDefault()
    setLoading(true)
    setStatus('')
    try {
      await api.post('/auth/2fa/confirm/', { code })
      setIsEnabled(true)
      setQrCode(null)
      setStatus('2FA activat cu succes!')
    } catch {
      setStatus('Cod invalid. Încearcă din nou.')
    } finally {
      setLoading(false)
    }
  }

  if (checking) {
    return (
      <div className="auth-wrap">
        <h1 className="auth-title">Autentificare în doi pași</h1>
        <p>Se verifică...</p>
      </div>
    )
  }

  return (
    <div className="auth-wrap">
      <h1 className="auth-title">Autentificare în doi pași</h1>

      {status && <div className="alert">{status}</div>}

      {isEnabled ? (
        <div className="alert alert-success">
          ✓ 2FA este activ pe acest cont. Ți se va cere codul la fiecare login.
        </div>
      ) : (
        <>
          {!qrCode && (
            <button className="btn-block" onClick={startSetup} disabled={loading}>
              {loading ? 'Se generează...' : 'Generează cod QR'}
            </button>
          )}

          {qrCode && (
            <>
              <p>Scanează codul cu Google Authenticator, Authy sau alt app similar:</p>
              <img src={qrCode} alt="QR Code 2FA" style={{ width: 200, height: 200 }} />
              <p style={{ fontSize: '0.8rem', wordBreak: 'break-all' }}>
                Sau introdu manual: <code>{secret}</code>
              </p>

              <form onSubmit={confirmCode}>
                <div className="form-field">
                  <label htmlFor="code">Cod din aplicație</label>
                  <input
                    id="code"
                    type="text"
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    maxLength={6}
                    required
                  />
                </div>
                <button className="btn-block" type="submit" disabled={loading}>
                  {loading ? 'Se verifică...' : 'Confirmă și activează'}
                </button>
              </form>
            </>
          )}
        </>
      )}
    </div>
  )
}