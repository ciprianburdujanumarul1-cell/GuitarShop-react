import { useEffect, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import api from '../api/client'
import { useCart } from '../context/CartContext'
import Footer from '../components/Footer'

export default function CheckoutSuccess() {
  const [searchParams] = useSearchParams()
  const sessionId = searchParams.get('session_id')
  const { clearCart } = useCart()
  const cleared = useRef(false)

  const [state, setState] = useState('loading') // 'loading' | 'paid' | 'unpaid' | 'error'
  const [order, setOrder] = useState(null)

  useEffect(() => {
    if (!sessionId) {
      setState('error')
      return
    }

    api
      .get(`/checkout/session/${sessionId}/`)
      .then(({ data }) => {
        setOrder(data)
        if (data.payment_status === 'paid') {
          setState('paid')
          // Only clear the cart once, and only once Stripe confirms payment.
          if (!cleared.current) {
            cleared.current = true
            clearCart()
          }
        } else {
          setState('unpaid')
        }
      })
      .catch(() => setState('error'))
  }, [sessionId, clearCart])

  return (
    <>
      <div className="page-wrap" style={{ textAlign: 'center' }}>
        {state === 'loading' && <div className="center-loading">Confirmăm plata…</div>}

        {state === 'paid' && (
          <>
            <h1 className="page-title">Comandă <span>confirmată!</span></h1>
            <p style={{ color: 'var(--muted)', marginBottom: 24 }}>
              Mulțumim pentru comandă! Am trimis o confirmare la {order?.customer_email || 'adresa ta de email'}.
            </p>
            {order?.amount_total != null && (
              <div className="alert alert-success" style={{ display: 'inline-block' }}>
                Total plătit: {order.amount_total.toFixed(2)} {order.currency?.toUpperCase()}
              </div>
            )}
            <div style={{ marginTop: 30 }}>
              <Link to="/" className="btn-block" style={{ display: 'inline-block', maxWidth: 260 }}>
                Continuă cumpărăturile
              </Link>
            </div>
          </>
        )}

        {state === 'unpaid' && (
          <>
            <h1 className="page-title">Plată <span>neconfirmată</span></h1>
            <p style={{ color: 'var(--muted)' }}>
              Plata nu a fost încă confirmată. Dacă ai finalizat achitarea, revino peste câteva momente.
            </p>
            <Link to="/cart" style={{ color: 'var(--accent)' }}>Înapoi la coș</Link>
          </>
        )}

        {state === 'error' && (
          <>
            <h1 className="page-title">Ceva nu a <span>mers bine</span></h1>
            <p style={{ color: 'var(--muted)' }}>
              Nu am putut confirma această sesiune de plată.
            </p>
            <Link to="/cart" style={{ color: 'var(--accent)' }}>Înapoi la coș</Link>
          </>
        )}
      </div>
      <Footer />
    </>
  )
}
