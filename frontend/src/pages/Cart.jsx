import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/client'
import { useCart } from '../context/CartContext'
import Footer from '../components/Footer'

export default function Cart() {
  const { cart, updateQty, removeFromCart } = useCart()
  const [quote, setQuote] = useState(null)
  const [loading, setLoading] = useState(true)
  const [status, setStatus] = useState(null) // { type: 'success'|'error', message }
  const [placing, setPlacing] = useState(false)

  useEffect(() => {
    const items = Object.keys(cart).length
    if (items === 0) {
      setQuote({ items: [], subtotal: '0.00', vat: '0.00', total: '0.00' })
      setLoading(false)
      return
    }
    setLoading(true)
    api
      .post('/cart/quote/', { items: cart })
      .then(({ data }) => setQuote(data))
      .finally(() => setLoading(false))
  }, [cart])

  async function placeOrder() {
    setPlacing(true)
    setStatus(null)
    try {
      const { data } = await api.post('/cart/checkout/', { items: cart })
      // Hand off to Stripe's hosted checkout page. The cart itself is only
      // cleared once /checkout/success confirms the payment went through.
      window.location.href = data.checkout_url
    } catch (err) {
      setStatus({ type: 'error', message: err.response?.data?.detail || 'A apărut o eroare.' })
      setPlacing(false)
    }
  }

  if (loading) return <div className="center-loading">Loading…</div>

  return (
    <>
      <div className="page-wrap">
        <h1 className="page-title">Your <span>Cart</span></h1>

        {status && (
          <div className={`alert ${status.type === 'success' ? 'alert-success' : 'alert-error'}`}>
            {status.message}
          </div>
        )}

        {quote.items.length === 0 ? (
          <p style={{ color: 'var(--muted)' }}>
            Your cart is empty. <Link to="/" style={{ color: 'var(--accent)' }}>Continue shopping</Link>
          </p>
        ) : (
          <>
            {quote.items.map(({ product, qty, line_total }) => (
              <div className="cart-row" key={product.id}>
                <img src={product.image || 'https://via.placeholder.com/80'} alt={product.name} />
                <div className="cart-row-info">
                  <div className="cart-row-name">{product.name}</div>
                  <div className="cart-row-price">{product.price} € each</div>
                </div>
                <div className="qty-control">
                  <button onClick={() => updateQty(product.id, 'decrease')}>−</button>
                  <span>{qty}</span>
                  <button onClick={() => updateQty(product.id, 'increase')}>+</button>
                </div>
                <div style={{ minWidth: 90, textAlign: 'right' }}>{line_total} €</div>
                <button className="remove-link" onClick={() => removeFromCart(product.id)}>Remove</button>
              </div>
            ))}

            <div className="cart-summary">
              <div className="summary-row">
                <span>Subtotal</span>
                <span>{quote.subtotal} €</span>
              </div>
              <div className="summary-row">
                <span>VAT (19%)</span>
                <span>{quote.vat} €</span>
              </div>
              <div className="summary-row total">
                <span>Total</span>
                <span>{quote.total} €</span>
              </div>
            </div>

            <button
              className="btn-block"
              style={{ marginTop: 24, maxWidth: 260 }}
              onClick={placeOrder}
              disabled={placing}
            >
              {placing ? 'Placing order…' : 'Checkout'}
            </button>
          </>
        )}
      </div>

      <Footer />
    </>
  )
}
