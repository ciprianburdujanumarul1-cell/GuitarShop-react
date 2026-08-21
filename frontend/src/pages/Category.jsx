import { useParams, Link, Navigate } from 'react-router-dom'
import Footer from '../components/Footer'
import { CATEGORIES } from '../config/catalog'

export default function Category() {
  const { category } = useParams()
  const data = CATEGORIES[category]

  if (!data) return <Navigate to="/" replace />

  return (
    <>
      <div className="hero">
        <div className="hero-bg" style={{ backgroundImage: `url('${data.heroImage}')` }} />
        <div className="hero-overlay" />
        <div className="hero-content">
          <div className="hero-eyebrow">Shop by Brand</div>
          <h1>{data.heroTitle}</h1>
          <p className="hero-sub">Explore premium {data.label.toLowerCase()} guitars</p>
        </div>
      </div>

      <div className="section-header">
        <div className="section-title">Brands</div>
        <div className="section-count">{data.brands.length} BRANDS</div>
      </div>
      <div className="divider" />

      <div className="products-grid">
        {data.brands.map((brand) => (
          <div className="card" key={brand.slug}>
            <div className="card-img-wrap">
              <img src={brand.image} alt={brand.name} />
            </div>
            <div className="card-body">
              <div className="card-name">{brand.name}</div>
              <div className="card-desc">{brand.desc}</div>
              <div className="card-footer">
                <Link to={`/products/${brand.slug}`} className="card-btn">Products</Link>
                <div className="card-arrow">→</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <Footer />
    </>
  )
}
