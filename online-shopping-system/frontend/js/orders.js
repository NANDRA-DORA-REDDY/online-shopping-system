async function loadOrders() {
  const customer = requireLogin();
  if (!customer) return;

  const container = document.getElementById("orders-list");
  container.innerHTML = `<div class="loading">Loading orders...</div>`;

  try {
    const orders = await apiFetch(`/orders/${customer.Customer_ID}`);

    if (!orders.length) {
      container.innerHTML = `
        <div class="order-card empty">
          <h3>No orders yet.</h3>
          <a class="btn primary" href="/products.html">Start Shopping</a>
        </div>`;
      return;
    }

    container.innerHTML = orders.map(order => `
      <article class="order-card">
        <div class="order-header">
          <div>
            <strong>Order #${order.Order_ID}</strong>
            <div class="muted">${order.Order_Date}</div>
          </div>
          <span class="status">${escapeHtml(order.Order_Status)}</span>
        </div>

        <div class="order-items">
          ${order.items.map(item => `
            <div class="order-item">
              <span>${escapeHtml(item.Product_Name)} × ${item.Quantity}</span>
              <strong>₹${(Number(item.Price) * item.Quantity).toFixed(2)}</strong>
            </div>
          `).join("")}
        </div>

        <div class="summary-row total">
          <span>Total</span>
          <span>₹${Number(order.Total_Amount).toFixed(2)}</span>
        </div>

        <div class="order-items">
          <div class="order-item">
            <span>Payment</span>
            <span>${escapeHtml(order.Payment_Method || "—")} / ${escapeHtml(order.Payment_Status || "—")}</span>
          </div>
          <div class="order-item">
            <span>Delivery</span>
            <span>${escapeHtml(order.Delivery_Status || "—")}</span>
          </div>
          <div class="order-item">
            <span>Address</span>
            <span>${escapeHtml(order.Delivery_Address || "—")}</span>
          </div>
        </div>
      </article>
    `).join("");
  } catch (error) {
    showMessage("orders-message", error.message, "error");
  }
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("orders-list")) loadOrders();
});
