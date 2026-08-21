import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/client'
import Footer from '../components/Footer'

export default function Wishlist() {
  const [items, setItems] = useState(null)

  useEffect(() => {
    api.get('/wishlist/').then(({ data }) => setItems(data))
  }, [])

  if (!items) return <div className="center-loading">Loading…</div>

  return (
    <>
      <div className="page-wrap">
        <h1 className="page-title">My <span>Favorites</span></h1>

        {items.length === 0 ? (
          <p style={{ color: 'var(--muted)' }}>
            No favorites yet. <Link to="/" style={{ color: 'var(--accent)' }}>Browse guitars</Link>
          </p>
        ) : (
          <div className="products-grid wrap">
            {items.map(({ product }) => (
              <Link to={`/product/${product.id}`} className="card" key={product.id}>
                <div className="card-img-wrap">
                  <img src={product.image || 'https://via.placeholder.com/300x250'} alt={product.name} />
                </div>
                <div className="card-body">
                  <div className="card-name">{product.name}</div>
                  <div className="card-desc">{product.price} €</div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      <Footer />
    </>
  )
}
