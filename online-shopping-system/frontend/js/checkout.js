async function loadCheckout() {
  const customer = requireLogin();
  if (!customer) return;

  const addressInput = document.getElementById("checkout-address");
  if (customer.Address) addressInput.value = customer.Address;

  try {
    const cart = await apiFetch(`/cart/${customer.Customer_ID}`);

    if (!cart.length) {
      showMessage("checkout-message", "Your cart is empty. Add a product first.", "error");
      document.getElementById("checkout-form").style.display = "none";
      return;
    }

    const total = cart.reduce((sum, item) => sum + Number(item.Subtotal), 0);
    document.getElementById("checkout-summary").innerHTML = `
      <div class="summary-row">
        <span>Products</span>
        <span>${cart.reduce((sum, item) => sum + item.Quantity, 0)}</span>
      </div>
      <div class="summary-row total">
        <span>Total</span>
        <span>₹${total.toFixed(2)}</span>
      </div>
    `;
  } catch (error) {
    showMessage("checkout-message", error.message, "error");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("checkout-form");
  if (!form) return;

  loadCheckout();

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const customer = requireLogin();
    if (!customer) return;

    const payload = {
      customer_id: customer.Customer_ID,
      address: document.getElementById("checkout-address").value.trim(),
      payment_method: document.getElementById("payment-method").value
    };

    try {
      const result = await apiFetch("/orders", {
        method: "POST",
        body: JSON.stringify(payload)
      });

      showMessage(
        "checkout-message",
        `Order #${result.order_id} placed successfully. Total: ₹${Number(result.total_amount).toFixed(2)}`,
        "success"
      );

      form.reset();
      setTimeout(() => {
        window.location.href = "/orders.html";
      }, 1200);
    } catch (error) {
      showMessage("checkout-message", error.message, "error");
    }
  });
});
