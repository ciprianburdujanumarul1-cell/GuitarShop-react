import { useEffect, useState } from 'react'
import { useParams, useSearchParams, Link } from 'react-router-dom'
import api from '../api/client'
import Footer from '../components/Footer'

export default function Products() {
  const { brand } = useParams()
  const [searchParams, setSearchParams] = useSearchParams()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [queryInput, setQueryInput] = useState(searchParams.get('q') || '')

  const shape = searchParams.get('shape') || ''
  const query = searchParams.get('q') || ''

  useEffect(() => {
    setLoading(true)
    api
      .get(`/products/${brand}/`, { params: { shape, q: query } })
      .then(({ data }) => setData(data))
      .finally(() => setLoading(false))
  }, [brand, shape, query])

  function submitSearch(e) {
    e.preventDefault()
    const next = new URLSearchParams()
    if (shape) next.set('shape', shape)
    if (queryInput) next.set('q', queryInput)
    setSearchParams(next)
  }

  function selectShape(nextShape) {
    const next = new URLSearchParams()
    if (nextShape) next.set('shape', nextShape)
    if (query) next.set('q', query)
    setSearchParams(next)
  }

  return (
    <>
      <div className="hero hero-sm">
        <div
          className="hero-bg"
          style={{ backgroundImage: "url('https://images.unsplash.com/photo-1511379938547-c1f69419868d')" }}
        />
        <div className="hero-content">
          <h1 style={{ fontSize: 56 }}>{data?.brand || brand}</h1>
          <p>Explore premium guitars from this brand</p>
        </div>
      </div>

      <div className="controls">
        <form className="search-form" onSubmit={submitSearch}>
          <input
            type="text"
            placeholder="Search guitars..."
            value={queryInput}
            onChange={(e) => setQueryInput(e.target.value)}
          />
          <button type="submit">⌕</button>
        </form>

        <div className="filter-bar">
          <button className={`filter-btn ${!shape ? 'active' : ''}`} onClick={() => selectShape('')}>
            All
          </button>
          {data?.shapes.map((s) => (
            <button
              key={s}
              className={`filter-btn ${shape === s ? 'active' : ''}`}
              onClick={() => selectShape(s)}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="center-loading">Loading…</div>
      ) : (
        <div className="products-grid wrap">
          {data.products.length === 0 && <p className="empty-msg">No products found.</p>}
          {data.products.map((product) => (
            <div className="card" key={product.id}>
              <div className="card-img-wrap">
                <img src={product.image || 'https://via.placeholder.com/300x250'} alt={product.name} />
              </div>
              <div className="card-body">
                <div className="card-name">{product.name}</div>
                <div className="card-desc">{product.price} €</div>
                <div className="card-footer">
                  <Link to={`/product/${product.id}`} className="card-btn">View</Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <Footer />
    </>
  )
}
