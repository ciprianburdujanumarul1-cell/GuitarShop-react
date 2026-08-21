import { Link } from 'react-router-dom'
import Footer from '../components/Footer'

export default function CheckoutCancel() {
  return (
    <>
      <div className="page-wrap" style={{ textAlign: 'center' }}>
        <h1 className="page-title">Plată <span>anulată</span></h1>
        <p style={{ color: 'var(--muted)', marginBottom: 24 }}>
          Nicio problemă — coșul tău e neschimbat, poți relua plata oricând.
        </p>
        <Link to="/cart" className="btn-block" style={{ display: 'inline-block', maxWidth: 260 }}>
          Înapoi la coș
        </Link>
      </div>
      <Footer />
    </>
  )
}
