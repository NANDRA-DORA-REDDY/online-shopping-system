async function loadCart() {
  const customer = requireLogin();
  if (!customer) return;

  const content = document.getElementById("cart-content");
  content.innerHTML = `<div class="loading">Loading cart...</div>`;

  try {
    const cart = await apiFetch(`/cart/${customer.Customer_ID}`);

    if (!cart.length) {
      content.innerHTML = `
        <div class="cart-card empty">
          <h3>Your cart is empty.</h3>
          <p>Add products before checkout.</p>
          <a class="btn primary" href="/products.html">Browse Products</a>
        </div>`;
      return;
    }

    const total = cart.reduce((sum, item) => sum + Number(item.Subtotal), 0);

    content.innerHTML = `
      <div class="cart-layout">
        <div>
          ${cart.map(item => `
            <div class="cart-card">
              <div class="cart-item">
                <div>
                  <h3>${escapeHtml(item.Product_Name)}</h3>
                  <p>₹${Number(item.Price).toFixed(2)} each</p>
                </div>
                <div class="qty-control">
                  <button onclick="changeQuantity(${item.Cart_ID}, ${item.Quantity - 1})">−</button>
                  <strong>${item.Quantity}</strong>
                  <button onclick="changeQuantity(${item.Cart_ID}, ${item.Quantity + 1})">+</button>
                </div>
                <strong>₹${Number(item.Subtotal).toFixed(2)}</strong>
                <button class="btn danger" onclick="removeCartItem(${item.Cart_ID})">Remove</button>
              </div>
            </div>
          `).join("")}
        </div>

        <aside class="cart-card">
          <h3>Order Summary</h3>
          <div class="summary-row">
            <span>Items</span><span>${cart.reduce((sum, item) => sum + item.Quantity, 0)}</span>
          </div>
          <div class="summary-row total">
            <span>Total</span><span>₹${total.toFixed(2)}</span>
          </div>
          <a class="btn primary full" href="/checkout.html">Proceed to Checkout</a>
        </aside>
      </div>
    `;
  } catch (error) {
    showMessage("cart-message", error.message, "error");
  }
}

async function changeQuantity(cartId, quantity) {
  if (quantity < 1) return removeCartItem(cartId);

  try {
    await apiFetch(`/cart/${cartId}`, {
      method: "PUT",
      body: JSON.stringify({ quantity })
    });
    await loadCart();
    updateCartCount();
  } catch (error) {
    showMessage("cart-message", error.message, "error");
  }
}

async function removeCartItem(cartId) {
  try {
    await apiFetch(`/cart/${cartId}`, { method: "DELETE" });
    await loadCart();
    updateCartCount();
  } catch (error) {
    showMessage("cart-message", error.message, "error");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("cart-content")) loadCart();
});
