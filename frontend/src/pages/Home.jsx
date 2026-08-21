import { Link } from 'react-router-dom'
import Footer from '../components/Footer'

const CATEGORY_CARDS = [
  {
    to: '/electric',
    badge: 'Electric',
    name: 'Electric Guitar',
    desc: 'High-output pickups, fast necks, and aggressive tones built for every style.',
    image: 'https://cdn.connectsites.net/user_files/esp/articles/002/014/603/original.jpg?1609774690&height=1200&width=1200',
  },
  {
    to: '/acoustic',
    badge: 'Acoustic',
    name: 'Acoustic Guitar',
    desc: 'Natural resonance and rich warmth — from parlour to dreadnought.',
    image: 'https://guitarfactory.net/cdn/shop/collections/Menu-Guitars-Acoustic-004.jpg?v=1711515615',
  },
  {
    to: '/bass',
    badge: 'Bass',
    name: 'Bass Guitar',
    desc: 'Lock in the groove. Active and passive options across all price ranges.',
    image: 'https://www.normans.co.uk/cdn/shop/products/B097HR1LDT.PT05_800x.jpg?v=1689946162',
  },
]

export default function Home() {
  return (
    <>
      <div className="hero">
        <div
          className="hero-bg"
          style={{ backgroundImage: "url('https://images.unsplash.com/photo-1511379938547-c1f69419868d')" }}
        />
        <div className="hero-overlay" />
        <div className="hero-content">
          <div className="hero-eyebrow">Est. 2010 — Premium Instruments</div>
          <h1>
            Best
            <br />
            <em>Guitar Store</em>
          </h1>
          <p className="hero-sub">Electric &nbsp;·&nbsp; Acoustic &nbsp;·&nbsp; Bass</p>
        </div>
      </div>

      <div className="section-header">
        <div className="section-title">Shop by Category</div>
        <div className="section-count">{CATEGORY_CARDS.length} CATEGORIES</div>
      </div>
      <div className="divider" />

      <div className="products-grid">
        {CATEGORY_CARDS.map((cat) => (
          <div className="card" key={cat.to}>
            <div className="card-img-wrap">
              <img src={cat.image} alt={cat.name} />
              <div className="card-badge">{cat.badge}</div>
            </div>
            <div className="card-body">
              <div className="card-name">{cat.name}</div>
              <div className="card-desc">{cat.desc}</div>
              <div className="card-footer">
                <Link to={cat.to} className="card-btn">Buy</Link>
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
