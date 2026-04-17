const state = {
    products: window.__INITIAL_DATA__.products || [],
    cart: window.__INITIAL_DATA__.cart || [],
    overview: window.__INITIAL_DATA__.overview || {},
};

const statusText = document.getElementById("status-text");
const cartList = document.getElementById("cart-list");
const cartCountChip = document.getElementById("cart-count-chip");
const cartTotalText = document.getElementById("cart-total-text");
const chatStream = document.getElementById("chat-stream");
const chatbotPanel = document.getElementById("chatbot-panel");

function currency(value) {
    return `Rs. ${value}`;
}

function setStatus(message, isError = false) {
    statusText.textContent = message;
    statusText.style.color = isError ? "#992f2f" : "";
}

function updateOverview(overview) {
    state.overview = overview;
    document.getElementById("overview-product-count").textContent = overview.product_count;
    document.getElementById("overview-available-units").textContent = overview.available_units;
    document.getElementById("overview-cart-items").textContent = overview.cart_items;
    document.getElementById("overview-cart-total").textContent = currency(overview.cart_total);
    cartCountChip.textContent = `${overview.cart_items} items`;
    cartTotalText.textContent = currency(overview.cart_total);
}

function renderCart() {
    if (!state.cart.length) {
        cartList.innerHTML = `<p class="empty-copy">The cart is empty. Add products from the dashboard to start an order.</p>`;
        return;
    }

    cartList.innerHTML = state.cart
        .map(
            (item) => `
                <article class="cart-item">
                    <strong>${item.product}</strong>
                    <span>Quantity: ${item.qty}</span>
                </article>
            `
        )
        .join("");
}

function updateProductStocks(products) {
    state.products = products;

    products.forEach((product) => {
        const stockTarget = document.querySelector(`[data-stock="${product.name}"]`);
        const card = document.querySelector(`[data-product-card="${product.name}"]`);
        const addButton = document.querySelector(`[data-add-product="${product.name}"]`);

        if (stockTarget) {
            stockTarget.textContent = product.stock;
        }

        if (card) {
            const stockBadge = card.querySelector(".stock-badge");
            stockBadge.classList.toggle("out", product.stock === 0);
        }

        if (addButton) {
            addButton.disabled = product.stock === 0;
            addButton.textContent = product.stock === 0 ? "Out Of Stock" : "Add To Cart";
            addButton.style.opacity = product.stock === 0 ? "0.55" : "1";
        }
    });
}

async function refreshDashboard() {
    const response = await fetch("/dashboard-data");
    const data = await response.json();
    state.cart = data.cart;
    updateOverview(data.overview);
    updateProductStocks(data.products);
    renderCart();
}

async function addToCart(productName) {
    const select = document.querySelector(`[data-qty-select="${productName}"]`);
    const qty = Number(select ? select.value : 1);

    const response = await fetch("/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product: productName, qty }),
    });

    const result = await response.json();

    if (!response.ok) {
        setStatus(result.msg || "Unable to add product.", true);
        return;
    }

    setStatus(`${productName} added to cart successfully.`);
    await refreshDashboard();
}

async function checkout() {
    const response = await fetch("/checkout");
    const result = await response.json();

    if (!response.ok) {
        setStatus(result.msg || "Checkout failed.", true);
        return;
    }

    setStatus("Order placed successfully.");
    await refreshDashboard();
}

function appendChatMessage(title, message, items = [], type = "bot") {
    const wrapper = document.createElement("article");
    wrapper.className = `chat-message ${type}`;

    const listMarkup = items.length
        ? `<ul>${items.map((item) => `<li>${item}</li>`).join("")}</ul>`
        : "";

    wrapper.innerHTML = `
        <h3>${title}</h3>
        <p>${message}</p>
        ${listMarkup}
    `;

    chatStream.appendChild(wrapper);
    chatStream.scrollTop = chatStream.scrollHeight;
}

async function runChatAction(action) {
    const labels = {
        show_products: "Show products",
        show_cart: "Show cart",
        show_best_value: "Suggest budget item",
        delivery_help: "Delivery help",
    };

    openChatbot();
    appendChatMessage("You selected", labels[action] || "Quick action", [], "user");

    const response = await fetch("/chatbot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action }),
    });

    const result = await response.json();
    appendChatMessage(result.title, result.message, result.items || []);
}

function openChatbot() {
    chatbotPanel.classList.add("open");
    chatbotPanel.setAttribute("aria-hidden", "false");
}

function closeChatbot() {
    chatbotPanel.classList.remove("open");
    chatbotPanel.setAttribute("aria-hidden", "true");
}

document.querySelectorAll("[data-add-product]").forEach((button) => {
    button.addEventListener("click", () => addToCart(button.dataset.addProduct));
});

document.getElementById("checkout-btn").addEventListener("click", checkout);
document.getElementById("chatbot-toggle").addEventListener("click", openChatbot);
document.getElementById("open-chatbot-hero").addEventListener("click", openChatbot);
document.getElementById("close-chatbot").addEventListener("click", closeChatbot);

document.querySelectorAll(".helper-action").forEach((button) => {
    button.addEventListener("click", () => runChatAction(button.dataset.chatAction));
});

document.querySelectorAll("[data-scroll-target]").forEach((button) => {
    button.addEventListener("click", () => {
        const target = document.getElementById(button.dataset.scrollTarget);
        if (target) {
            target.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    });
});

renderCart();
