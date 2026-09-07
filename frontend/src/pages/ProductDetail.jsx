import { Fragment, useEffect, useRef, useState } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../api/client";
import { useCart } from "../context/CartContext";
import Footer from "../components/Footer";

const WS_URL = import.meta.env.VITE_WS_URL || "ws://127.0.0.1:8000";

function starsHtml(rating) {
  return "★★★★★☆☆☆☆☆".slice(5 - rating, 10 - rating);
}

export default function ProductDetail() {
  const { id } = useParams();
  const { addToCart } = useCart();

  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [favorited, setFavorited] = useState(false);
  const [heartPulse, setHeartPulse] = useState(false);
  const [reviews, setReviews] = useState([]);
  const [message, setMessage] = useState("");
  const [rating, setRating] = useState(5);
  const [added, setAdded] = useState(false);

  const socketRef = useRef(null);
  const addBtnRef = useRef(null);
  const cartIconRef = useRef(null);

  useEffect(() => {
    setLoading(true);
    api.get(`/products/detail/${id}/`).then(({ data }) => {
      setProduct(data);
      setFavorited(data.is_favorited);
      setReviews(data.reviews);
      setLoading(false);
    });
  }, [id]);

  // ── Live reviews over WebSocket ──
  useEffect(() => {
    const token = localStorage.getItem("access");
    const socket = new WebSocket(
      `${WS_URL}/ws/socket-server/${id}/?token=${token}`,
    );
    socketRef.current = socket;
    socket.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.type === "chat") {
        setReviews((prev) => [
          {
            id: `live-${Date.now()}`,
            username: data.username,
            message: data.message,
            rating: data.rating,
            created_at: new Date().toISOString(),
          },
          ...prev,
        ]);
      }
    };

    return () => socket.close();
  }, [id]);

  function submitReview(e) {
    e.preventDefault();
    if (!message.trim() || !socketRef.current) return;
    socketRef.current.send(
      JSON.stringify({
        message: message.trim(),
        rating,
        // username eliminat: serverul îl ia din tokenul JWT verificat în
        // asgi.py / jwt_auth_middleware.py — nu mai are rost și nu mai
        // trebuie să aibă încredere în ce trimite clientul.
      }),
    );
    setMessage("");
  }

  async function toggleWishlist() {
    try {
      const { data } = await api.post(`/wishlist/toggle/${id}/`);
      setFavorited(data.favorited);
      setHeartPulse(true);
      setTimeout(() => setHeartPulse(false), 350);
    } catch (err) {
      console.error("Wishlist toggle failed:", err);
    }
  }

  function flyToCart() {
    const startEl = addBtnRef.current;
    const endEl = cartIconRef.current;
    if (!startEl || !endEl) return;

    const startRect = startEl.getBoundingClientRect();
    const endRect = endEl.getBoundingClientRect();

    const dot = document.createElement("div");
    dot.className = "fly-dot";
    dot.style.left = `${startRect.left + startRect.width / 2 - 7}px`;
    dot.style.top = `${startRect.top + startRect.height / 2 - 7}px`;
    document.body.appendChild(dot);

    requestAnimationFrame(() => {
      const dx =
        endRect.left +
        endRect.width / 2 -
        (startRect.left + startRect.width / 2);
      const dy =
        endRect.top +
        endRect.height / 2 -
        (startRect.top + startRect.height / 2);
      dot.style.transform = `translate(${dx}px, ${dy}px) scale(0.3)`;
      dot.style.opacity = "0.2";
    });

    dot.addEventListener(
      "transitionend",
      () => {
        dot.remove();
        endEl.classList.remove("shake");
        void endEl.offsetWidth;
        endEl.classList.add("shake");
      },
      { once: true },
    );
  }

  function handleAddToCart() {
    if (!product?.is_in_stock) return;
    addToCart(product.id, product.stock);
    setAdded(true);
    flyToCart();
    setTimeout(() => setAdded(false), 900);
  }

  if (loading) return <div className="center-loading">Loading…</div>;
  if (!product) return <div className="center-loading">Product not found.</div>;

  return (
    <>
      <div className="pd-container">
        <div className="pd-image">
          <img
            src={product.image || "https://via.placeholder.com/450x400"}
            alt={product.name}
          />
        </div>

        <div className="pd-info">
          <div className="pd-name">{product.name}</div>
          <div className="pd-price">{product.price} €</div>

          {product.avg_rating && (
            <div className="avg-rating">
              <span className="stars">
                {starsHtml(Math.round(product.avg_rating))}
              </span>
              <span className="count">
                {product.avg_rating} · {product.review_count} review
                {product.review_count !== 1 ? "s" : ""}
              </span>
            </div>
          )}

          <div className="pd-description">
            Body | {product.body}
            <br />
            Neck | {product.neck}
            <br />
            Grip Shape | {product.grip_shape}
            <br />
            Fingerboard | {product.fingerboard}
            <br />
            Fret | {product.fret}
            <br />
            Inlay | {product.inlay}
            <br />
            Scale | {product.scale}
            <br />
            Nut | {product.nut}
            <br />
            Construction | {product.construction}
            <br />
            Tuner | {product.tuner}
            <br />
            Bridge | {product.bridge}
            <br />
            Pickup | {product.pickup}
            <br />
            Controls | {product.controls}
            <br />
            Color | {product.color}
          </div>

          <div
            style={{
              display: "flex",
              gap: 12,
              alignItems: "center",
              marginBottom: 16,
            }}
          >
            {product.is_in_stock ? (
              <button
                ref={addBtnRef}
                className={`btn-primary ${added ? "added" : ""}`}
                onClick={handleAddToCart}
              >
                {added ? "Added ✓" : "Add to Cart"}
              </button>
            ) : (
              <>
                <p className="out-of-stock">Out of stock</p>
                <button className="btn-primary" disabled>
                  Add to Cart
                </button>
              </>
            )}

            <button
              ref={cartIconRef}
              className="icon-wrap"
              onClick={() => (window.location.href = "/cart")}
              aria-label="Go to cart"
              type="button"
            >
              <svg viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M3 3h2l.4 2M7 13h10l3-8H5.4M7 13L5.4 5M7 13l-1.5 6h11.5M9 21a1 1 0 100-2 1 1 0 000 2zm8 0a1 1 0 100-2 1 1 0 000 2z"
                />
              </svg>
            </button>

            <button
              className={`icon-wrap ${favorited ? "favorited" : ""} ${heartPulse ? "pulse" : ""}`}
              onClick={toggleWishlist}
              aria-label="Add to wishlist"
              type="button"
            >
              <svg viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M12 21s-7.5-4.6-10-9.3C.4 8.2 2.3 4.5 6 4c2-.3 3.8.8 6 3.1C14.2 4.8 16 3.7 18 4c3.7.5 5.6 4.2 4 7.7C19.5 16.4 12 21 12 21z"
                />
              </svg>
            </button>
            <Link
              to="/wishlist"
              style={{ fontSize: 13, color: "var(--muted)" }}
            >
              My Favorites
            </Link>
          </div>
        </div>

        {/* REVIEWS */}
        <div className="reviews-section">
          <h2>
            Re<span>views</span>
          </h2>

          <form className="review-form" onSubmit={submitReview}>
            <div className="star-rating">
              {[5, 4, 3, 2, 1].map((n) => (
                <Fragment key={n}>
                  <input
                    type="radio"
                    name="rating"
                    id={`star-${n}`}
                    value={n}
                    checked={rating === n}
                    onChange={() => setRating(n)}
                  />
                  <label htmlFor={`star-${n}`}>★</label>
                </Fragment>
              ))}
            </div>
            <div className="review-form-row">
              <input
                type="text"
                placeholder="Leave a review…"
                autoComplete="off"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
              />
              <button type="submit" className="btn-primary">
                Post Review
              </button>
            </div>
          </form>

          <div className="messages-list">
            {reviews.length === 0 && (
              <p className="no-reviews">No reviews yet. Be the first!</p>
            )}
            {reviews.map((review) => (
              <div className="review-card" key={review.id}>
                <div className="review-meta">
                  {review.username} ·{" "}
                  {new Date(review.created_at).toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </div>
                <div className="review-stars">{starsHtml(review.rating)}</div>
                <p>{review.message}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <Footer />
    </>
  );
}