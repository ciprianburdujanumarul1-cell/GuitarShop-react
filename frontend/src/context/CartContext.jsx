import { createContext, useContext, useEffect, useState, useCallback } from 'react'

const CartContext = createContext(null)
const STORAGE_KEY = 'guitarshop_cart' // { [productId]: qty }

function readCart() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {}
  } catch {
    return {}
  }
}

export function CartProvider({ children }) {
  const [cart, setCart] = useState(readCart)

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(cart))
  }, [cart])

  const addToCart = useCallback((productId, stock) => {
    setCart((prev) => {
      const key = String(productId)
      const current = prev[key] || 0
      if (stock != null && current + 1 > stock) return prev
      return { ...prev, [key]: current + 1 }
    })
  }, [])

  const updateQty = useCallback((productId, action) => {
    setCart((prev) => {
      const key = String(productId)
      const next = { ...prev }
      const current = next[key] || 0
      if (action === 'increase') {
        next[key] = current + 1
      } else if (action === 'decrease') {
        if (current - 1 <= 0) delete next[key]
        else next[key] = current - 1
      }
      return next
    })
  }, [])

  const removeFromCart = useCallback((productId) => {
    setCart((prev) => {
      const next = { ...prev }
      delete next[String(productId)]
      return next
    })
  }, [])

  const clearCart = useCallback(() => setCart({}), [])

  const count = Object.values(cart).reduce((sum, qty) => sum + qty, 0)

  return (
    <CartContext.Provider
      value={{ cart, count, addToCart, updateQty, removeFromCart, clearCart }}
    >
      {children}
    </CartContext.Provider>
  )
}

export function useCart() {
  const ctx = useContext(CartContext)
  if (!ctx) throw new Error('useCart must be used within CartProvider')
  return ctx
}
