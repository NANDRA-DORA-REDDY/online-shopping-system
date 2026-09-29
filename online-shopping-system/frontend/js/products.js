let allProducts = [];

async function loadCategories() {
  const categories = await apiFetch("/categories");
  const select = document.getElementById("category-filter");

  categories.forEach(category => {
    const option = document.createElement("option");
    option.value = category.Category_ID;
    option.textContent = category.Category_Name;
    select.appendChild(option);
  });
}

async function loadProducts() {
  const search = document.getElementById("product-search").value.trim();
  const category = document.getElementById("category-filter").value;

  const params = new URLSearchParams();
  if (search) params.set("search", search);
  if (category) params.set("category_id", category);

  const grid = document.getElementById("product-grid");
  grid.innerHTML = `<div class="loading">Loading products...</div>`;

  try {
    allProducts = await apiFetch(`/products?${params.toString()}`);
    renderProducts(allProducts);
  } catch (error) {
    grid.innerHTML = `<div class="empty">${error.message}</div>`;
  }
}

function renderProducts(products) {
  const grid = document.getElementById("product-grid");

  if (!products.length) {
    grid.innerHTML = `<div class="empty">No products found.</div>`;
    return;
  }

  grid.innerHTML = products.map(product => {
    const icon = product.Category_Name === "Electronics" ? "🎧" :
                 product.Category_Name === "Accessories" ? "🖱️" : "🏠";

    return `
      <article class="product-card">
        <div class="product-image">${icon}</div>
        <div class="product-body">
          <div class="product-category">${escapeHtml(product.Category_Name)}</div>
          <h3>${escapeHtml(product.Product_Name)}</h3>
          <div class="price">₹${Number(product.Price).toFixed(2)}</div>
          <div class="stock">${product.Stock > 0 ? `${product.Stock} in stock` : "Out of stock"}</div>
          <button class="btn primary full"
            ${product.Stock < 1 ? "disabled" : ""}
            onclick="addToCart(${product.Product_ID})">
            Add to Cart
          </button>
        </div>
      </article>
    `;
  }).join("");
}

async function addToCart(productId) {
  const customer = requireLogin();
  if (!customer) return;

  try {
    await apiFetch("/cart", {
      method: "POST",
      body: JSON.stringify({
        customer_id: customer.Customer_ID,
        product_id: productId,
        quantity: 1
      })
    });

    showMessage("product-message", "Product added to your cart.", "success");
    updateCartCount();
  } catch (error) {
    showMessage("product-message", error.message, "error");
  }
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

document.addEventListener("DOMContentLoaded", async () => {
  if (!document.getElementById("product-grid")) return;

  try {
    await loadCategories();
    await loadProducts();
  } catch (error) {
    showMessage("product-message", error.message, "error");
  }

  document.getElementById("product-search")
    .addEventListener("input", loadProducts);

  document.getElementById("category-filter")
    .addEventListener("change", loadProducts);
});
