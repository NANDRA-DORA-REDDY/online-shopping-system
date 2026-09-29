const API = "/api";

function getCustomer() {
  try {
    return JSON.parse(localStorage.getItem("customer"));
  } catch {
    return null;
  }
}

function setCustomer(customer) {
  localStorage.setItem("customer", JSON.stringify(customer));
}

function logout() {
  localStorage.removeItem("customer");
  window.location.href = "/login.html";
}

function requireLogin() {
  const customer = getCustomer();
  if (!customer) {
    window.location.href = "/login.html";
    return null;
  }
  return customer;
}

async function apiFetch(path, options = {}) {
  const response = await fetch(API + path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options
  });

  let data = {};
  try { data = await response.json(); } catch {}

  if (!response.ok) {
    throw new Error(data.error || "Something went wrong.");
  }
  return data;
}

function showMessage(elementId, message, type = "") {
  const element = document.getElementById(elementId);
  if (!element) return;
  element.textContent = message;
  element.className = `message ${type}`;
}

async function updateCartCount() {
  const badge = document.getElementById("cart-count");
  const customer = getCustomer();
  if (!badge || !customer) {
    if (badge) badge.textContent = "0";
    return;
  }

  try {
    const cart = await apiFetch(`/cart/${customer.Customer_ID}`);
    badge.textContent = cart.reduce((sum, item) => sum + item.Quantity, 0);
  } catch {
    badge.textContent = "0";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const customer = getCustomer();
  const loginLink = document.getElementById("nav-login");
  const logoutBtn = document.getElementById("logout-btn");

  if (customer && loginLink) {
    loginLink.textContent = customer.Customer_Name;
    loginLink.href = "#";
  }

  if (logoutBtn) {
    if (customer) {
      logoutBtn.classList.remove("hidden");
      logoutBtn.addEventListener("click", logout);
    }
  }

  updateCartCount();

  const loginForm = document.getElementById("login-form");
  if (loginForm) {
    loginForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const email = document.getElementById("login-email").value.trim();

      try {
        const result = await apiFetch("/login", {
          method: "POST",
          body: JSON.stringify({ email })
        });
        setCustomer(result.customer);
        window.location.href = "/products.html";
      } catch (error) {
        showMessage("login-message", error.message, "error");
      }
    });
  }

  const registerForm = document.getElementById("register-form");
  if (registerForm) {
    registerForm.addEventListener("submit", async (event) => {
      event.preventDefault();

      const payload = {
        name: document.getElementById("register-name").value.trim(),
        email: document.getElementById("register-email").value.trim(),
        phone: document.getElementById("register-phone").value.trim(),
        address: document.getElementById("register-address").value.trim()
      };

      try {
        const result = await apiFetch("/register", {
          method: "POST",
          body: JSON.stringify(payload)
        });
        setCustomer(result.customer);
        window.location.href = "/products.html";
      } catch (error) {
        showMessage("register-message", error.message, "error");
      }
    });
  }
});
