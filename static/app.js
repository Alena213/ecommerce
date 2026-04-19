window.__INITIAL_DATA__ = window.__INITIAL_DATA__ || {
    products: [],
    cart: [],
    overview: {},
};

const state = {
    products: window.__INITIAL_DATA__.products || [],
    cart: window.__INITIAL_DATA__.cart || [],
    overview: window.__INITIAL_DATA__.overview || {},
};

function $(id) {
    return document.getElementById(id);
}

const statusText = $("status-text");
const cartList = $("cart-list");
const cartCountChip = $("cart-count-chip");
const cartTotalText = $("cart-total-text");
const chatStream = $("chat-stream");
const assistantSection = $("assistant-section");
const chatForm = $("chat-form");
const chatInput = $("chat-input");
const checkoutBtn = $("checkout-btn");

function currency(value) {
    return `Rs. ${value}`;
}

function escapeHtml(text) {
    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

function cssEscape(value) {
    if (typeof CSS !== "undefined" && typeof CSS.escape === "function") {
        return CSS.escape(value);
    }
    return String(value).replace(/\\/g, "\\\\").replace(/"/g, '\\"');
}

function setStatus(message, isError = false) {
    if (!statusText) {
        return;
    }
    statusText.textContent = message;
    statusText.style.color = isError ? "#b42318" : "";
}

function updateOverview(overview) {
    state.overview = overview;
    const productCount = $("overview-product-count");
    const availableUnits = $("overview-available-units");
    const cartItems = $("overview-cart-items");
    const cartTotal = $("overview-cart-total");
    if (productCount) {
        productCount.textContent = overview.product_count;
    }
    if (availableUnits) {
        availableUnits.textContent = overview.available_units;
    }
    if (cartItems) {
        cartItems.textContent = overview.cart_items;
    }
    if (cartTotal) {
        cartTotal.textContent = currency(overview.cart_total);
    }
    if (cartCountChip) {
        cartCountChip.textContent = `${overview.cart_items} items`;
    }
    if (cartTotalText) {
        cartTotalText.textContent = currency(overview.cart_total);
    }
}

function renderCart() {
    if (!cartList) {
        return;
    }
    if (!state.cart.length) {
        cartList.innerHTML = `<p class="empty-copy">The cart is empty. Add products from the dashboard to start an order.</p>`;
        return;
    }

    cartList.innerHTML = state.cart
        .map(
            (item) => `
                <article class="cart-item">
                    <strong>${escapeHtml(item.product)}</strong>
                    <span>Quantity: ${escapeHtml(item.qty)}</span>
                </article>
            `
        )
        .join("");
}

function updateProductStocks(products) {
    state.products = products;

    products.forEach((product) => {
        const safe = cssEscape(product.name);
        const stockTarget = document.querySelector(`[data-stock="${safe}"]`);
        const card = document.querySelector(`[data-product-card="${safe}"]`);
        const addButton = document.querySelector(`[data-add-product="${safe}"]`);

        if (stockTarget) {
            stockTarget.textContent = product.stock;
        }

        if (card) {
            const stockBadge = card.querySelector(".stock-badge");
            if (stockBadge) {
                stockBadge.classList.toggle("out", product.stock === 0);
            }
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
    const select = document.querySelector(`[data-qty-select="${cssEscape(productName)}"]`);
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

function scrollToAssistant() {
    if (assistantSection) {
        assistantSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }
}

function appendChatMessage(title, message, items = [], type = "bot") {
    if (!chatStream) {
        return;
    }

    const wrapper = document.createElement("article");
    wrapper.className = `chat-message ${type}`;

    const heading = document.createElement("h3");
    heading.textContent = title;
    wrapper.appendChild(heading);

    const safeMessage = typeof message === "string" ? message.trim() : "";
    if (safeMessage) {
        const paragraph = document.createElement("p");
        paragraph.textContent = safeMessage;
        wrapper.appendChild(paragraph);
    }

    if (items.length) {
        const list = document.createElement("ul");
        items.forEach((item) => {
            const li = document.createElement("li");
            li.textContent = item;
            list.appendChild(li);
        });
        wrapper.appendChild(list);
    }

    chatStream.appendChild(wrapper);
    chatStream.scrollTop = chatStream.scrollHeight;
}

async function parseJsonResponse(response) {
    const text = await response.text();
    try {
        return JSON.parse(text);
    } catch (error) {
        return {
            title: "Assistant",
            message: "Unexpected reply from server. Check that Flask is running and try again.",
            items: [text.slice(0, 200)],
        };
    }
}

async function runChatAction(action) {
    const labels = {
        show_products: "Show products",
        show_cart: "Show cart",
        show_best_value: "Suggest budget item",
        delivery_help: "Delivery help",
        checkout_help: "Checkout help",
        payment_help: "Payment options",
        return_help: "Return policy",
        show_status: "Store status",
        show_offers: "Today's offers",
    };

    scrollToAssistant();
    appendChatMessage("You selected", labels[action] || "Quick action", [], "user");

    if (!action) {
        appendChatMessage(
            "Assistant",
            "That button is missing an action. Check data-chat-action in index.html.",
            [],
            "bot"
        );
        return;
    }

    try {
        const response = await fetch("/chatbot", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action }),
        });

        const result = await parseJsonResponse(response);

        if (!response.ok) {
            appendChatMessage(
                "Assistant",
                result.message || "Request failed.",
                Array.isArray(result.items) ? result.items : [],
                "bot"
            );
            return;
        }

        appendChatMessage(
            result.title || "Assistant",
            result.message ?? "",
            Array.isArray(result.items) ? result.items : []
        );
    } catch (error) {
        appendChatMessage(
            "Assistant",
            "Could not reach the server. Run python app.py and refresh this page.",
            [],
            "bot"
        );
    }
}

async function sendChatMessage(message) {
    const trimmedMessage = message.trim();
    if (!trimmedMessage) {
        return;
    }

    scrollToAssistant();
    appendChatMessage("You asked", trimmedMessage, [], "user");

    try {
        const response = await fetch("/chatbot", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: trimmedMessage }),
        });

        const result = await parseJsonResponse(response);

        if (!response.ok) {
            appendChatMessage(
                "Assistant",
                result.message || "Request failed.",
                Array.isArray(result.items) ? result.items : [],
                "bot"
            );
            return;
        }

        appendChatMessage(
            result.title || "Assistant",
            result.message ?? "",
            Array.isArray(result.items) ? result.items : []
        );
    } catch (error) {
        appendChatMessage(
            "Assistant",
            "Could not reach the server. Run python app.py and refresh this page.",
            [],
            "bot"
        );
    }
}

function init() {
    document.querySelectorAll("[data-add-product]").forEach((button) => {
        button.addEventListener("click", () => addToCart(button.getAttribute("data-add-product")));
    });

    if (checkoutBtn) {
        checkoutBtn.addEventListener("click", checkout);
    }

    document.body.addEventListener("click", (event) => {
        const target = event.target.closest("[data-chat-action]");
        if (!target) {
            return;
        }
        const action = target.getAttribute("data-chat-action");
        if (action) {
            runChatAction(action);
        }
    });

    if (chatForm && chatInput) {
        chatForm.addEventListener("submit", async (event) => {
            event.preventDefault();
            const message = chatInput.value;
            chatInput.value = "";
            await sendChatMessage(message);
        });
    }

    document.querySelectorAll("[data-scroll-target]").forEach((button) => {
        button.addEventListener("click", () => {
            const targetId = button.getAttribute("data-scroll-target");
            const target = targetId ? document.getElementById(targetId) : null;
            if (target) {
                target.scrollIntoView({ behavior: "smooth", block: "start" });
            }
        });
    });

    renderCart();
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
} else {
    init();
}
