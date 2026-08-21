import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useCart } from '../context/CartContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const { count } = useCart()

  return (
    <nav className="nav">
      <Link to="/" className="nav-brand">
        🎸 Guitar<span>Shop</span>
      </Link>
      <div className="nav-links">
        <Link to="/">Home</Link>
        <a href="#">About</a>
        <a href="#">Services</a>
        <a href="#">Contact</a>

        <div className="nav-icons">
          <Link to="/wishlist" className="icon-wrap" aria-label="Wishlist" id="cart-icon">
            <svg viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 21s-7.5-4.6-10-9.3C.4 8.2 2.3 4.5 6 4c2-.3 3.8.8 6 3.1C14.2 4.8 16 3.7 18 4c3.7.5 5.6 4.2 4 7.7C19.5 16.4 12 21 12 21z"
              />
            </svg>
          </Link>
          <Link to="/cart" className="icon-wrap" aria-label="Cart">
            <svg viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M3 3h2l.4 2M7 13h10l3-8H5.4M7 13L5.4 5M7 13l-1.5 6h11.5M9 21a1 1 0 100-2 1 1 0 000 2zm8 0a1 1 0 100-2 1 1 0 000 2z"
              />
            </svg>
            <span className={`badge ${count ? '' : 'hidden'}`}>{count}</span>
          </Link>
        </div>

        <div className="nav-auth">
          {user ? (
            <>
              <span>Hello {user.username}</span>
              <button className="btn-filled" onClick={logout}>Logout</button>
            </>
          ) : (
            <>
              <Link to="/signin" className="btn-outline">Sign In</Link>
              <Link to="/login" className="btn-filled">Login</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
