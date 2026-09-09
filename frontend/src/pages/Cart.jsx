import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/client";
import { useCart } from "../context/CartContext";
import Footer from "../components/Footer";

const EMPTY_ADDRESS = {
  fullName: "",
  line1: "",
  line2: "",
  city: "",
  postalCode: "",
  country: "",
};

export default function Cart() {
  const { cart, updateQty, removeFromCart } = useCart();
  const [quote, setQuote] = useState(null);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState(null); // { type: 'success'|'error', message }
  const [placing, setPlacing] = useState(false);
  const [address, setAddress] = useState(EMPTY_ADDRESS);

  useEffect(() => {
    const items = Object.keys(cart).length;
    if (items === 0) {
      setQuote({
        items: [],
        subtotal: "0.00",
        vat: "0.00",
        vat_rate: "0",
        total: "0.00",
      });
      setLoading(false);
      return;
    }
    setLoading(true);
    api
      .post("/cart/quote/", { items: cart, country: address.country || null })
      .then(({ data }) => setQuote(data))
      .finally(() => setLoading(false));
  }, [cart, address.country]);

  function handleAddressChange(field) {
    return (e) => setAddress((prev) => ({ ...prev, [field]: e.target.value }));
  }

  function validateAddress() {
    const required = ["fullName", "line1", "city", "postalCode", "country"];
    const missing = required.filter((field) => !address[field].trim());
    return missing.length === 0;
  }

  async function placeOrder(e) {
    e.preventDefault();

    if (!validateAddress()) {
      setStatus({
        type: "error",
        message: "Please fill in all required address fields.",
      });
      return;
    }

    setPlacing(true);
    setStatus(null);
    try {
      const { data } = await api.post("/cart/checkout/", {
        items: cart,
        address,
      });
      // Hand off to Stripe's hosted checkout page. The cart itself is only
      // cleared once /checkout/success confirms the payment went through.
      window.location.href = data.checkout_url;
    } catch (err) {
      setStatus({
        type: "error",
        message: err.response?.data?.detail || "A apărut o eroare.",
      });
      setPlacing(false);
    }
  }

  if (loading) return <div className="center-loading">Loading…</div>;

  return (
    <>
      <div className="page-wrap">
        <h1 className="page-title">
          Your <span>Cart</span>
        </h1>

        {status && (
          <div
            className={`alert ${status.type === "success" ? "alert-success" : "alert-error"}`}
          >
            {status.message}
          </div>
        )}

        {quote.items.length === 0 ? (
          <p style={{ color: "var(--muted)" }}>
            Your cart is empty.{" "}
            <Link to="/" style={{ color: "var(--accent)" }}>
              Continue shopping
            </Link>
          </p>
        ) : (
          <>
            {quote.items.map(({ product, qty, line_total }) => (
              <div className="cart-row" key={product.id}>
                <img
                  src={product.image || "https://via.placeholder.com/80"}
                  alt={product.name}
                />
                <div className="cart-row-info">
                  <div className="cart-row-name">{product.name}</div>
                  <div className="cart-row-price">{product.price} € each</div>
                </div>
                <div className="qty-control">
                  <button onClick={() => updateQty(product.id, "decrease")}>
                    −
                  </button>
                  <span>{qty}</span>
                  <button onClick={() => updateQty(product.id, "increase")}>
                    +
                  </button>
                </div>
                <div style={{ minWidth: 90, textAlign: "right" }}>
                  {line_total} €
                </div>
                <button
                  className="remove-link"
                  onClick={() => removeFromCart(product.id)}
                >
                  Remove
                </button>
              </div>
            ))}

            <form onSubmit={placeOrder}>
              <div className="form-field" style={{ marginTop: 32 }}>
                <h2 style={{ marginBottom: 12 }}>Shipping Address</h2>

                <div style={{ display: "grid", gap: 12, maxWidth: 420 }}>
                  <input
                    type="text"
                    placeholder="Full name"
                    value={address.fullName}
                    onChange={handleAddressChange("fullName")}
                    required
                  />
                  <input
                    type="text"
                    placeholder="Address line 1"
                    value={address.line1}
                    onChange={handleAddressChange("line1")}
                    required
                  />
                  <input
                    type="text"
                    placeholder="Address line 2 (optional)"
                    value={address.line2}
                    onChange={handleAddressChange("line2")}
                  />
                  <div style={{ display: "flex", gap: 12 }}>
                    <input
                      type="text"
                      placeholder="City"
                      value={address.city}
                      onChange={handleAddressChange("city")}
                      required
                      style={{ flex: 2 }}
                    />
                    <input
                      type="text"
                      placeholder="Postal code"
                      value={address.postalCode}
                      onChange={handleAddressChange("postalCode")}
                      required
                      style={{ flex: 1 }}
                    />
                  </div>
                  <select
                    className="custom-scroll"
                    placeholder="Country"
                    value={address.country}
                    onChange={handleAddressChange("country")}
                    required
                  >
                    <option value="">Choose one</option>
                    <option value="md">Moldova</option>
                    <option value="at">Austria</option>
                    <option value="be">Belgium</option>
                    <option value="bg">Bulgaria</option>
                    <option value="hr">Croatia</option>
                    <option value="cy">Cyprus</option>
                    <option value="cz">Czech Republic</option>
                    <option value="dk">Denmark</option>
                    <option value="ee">Estonia</option>
                    <option value="fi">Finland</option>
                    <option value="fr">France</option>
                    <option value="de">Germany</option>
                    <option value="gr">Greece</option>
                    <option value="hu">Hungary</option>
                    <option value="ie">Ireland</option>
                    <option value="it">Italy</option>
                    <option value="lv">Latvia</option>
                    <option value="lt">Lithuania</option>
                    <option value="lu">Luxembourg</option>
                    <option value="mt">Malta</option>
                    <option value="nl">Netherlands</option>
                    <option value="pl">Poland</option>
                    <option value="pt">Portugal</option>
                    <option value="ro">Romania</option>
                    <option value="sk">Slovakia</option>
                    <option value="si">Slovenia</option>
                    <option value="es">Spain</option>
                    <option value="se">Sweden</option>
                  </select>
                </div>
              </div>

              <div className="form-field">
                <div className="cart-summary">
                  <div className="summary-row">
                    <span>Subtotal</span>
                    <span>{quote.subtotal} €</span>
                  </div>
                  <div className="summary-row">
                    <span>VAT ({quote.vat_rate}%)</span>
                    <span>{quote.vat} €</span>
                  </div>
                  <div className="summary-row total">
                    <span>Total</span>
                    <span>{quote.total} €</span>
                  </div>
                </div>

                <button
                  type="submit"
                  className="btn-block"
                  style={{ marginTop: 24, maxWidth: 260 }}
                  disabled={placing}
                >
                  {placing ? "Placing order…" : "Checkout"}
                </button>
              </div>
            </form>
          </>
        )}
      </div>

      <Footer />
    </>
  );
}
