import json
import os

from flask import Flask, jsonify, render_template, request


app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.json")


def load():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def build_cart_summary(db):
    price_map = {product["name"]: product["price"] for product in db["products"]}
    item_count = 0
    total = 0

    for item in db["cart"]:
        qty = int(item["qty"])
        item_count += qty
        total += price_map.get(item["product"], 0) * qty

    return {"item_count": item_count, "total": total}


def build_overview(db):
    cart_summary = build_cart_summary(db)
    return {
        "product_count": len(db["products"]),
        "available_units": sum(product["stock"] for product in db["products"]),
        "cart_items": cart_summary["item_count"],
        "cart_total": cart_summary["total"],
    }


def build_chat_response(action):
    db = load()
    products = db["products"]
    summary = build_cart_summary(db)

    if action == "show_products":
        lines = [
            f"{product['name']}: Rs. {product['price']} | Stock {product['stock']} | Delivery {product['delivery']}"
            for product in products
        ]
        return {
            "title": "Available products",
            "message": "Here is the current product catalog.",
            "items": lines,
        }

    if action == "show_best_value":
        cheapest = min(products, key=lambda product: product["price"])
        return {
            "title": "Best budget pick",
            "message": f"{cheapest['name']} is the lowest-priced item at Rs. {cheapest['price']}.",
            "items": [
                f"Specs: {cheapest['specs']}",
                f"Delivery: {cheapest['delivery']}",
                f"Stock left: {cheapest['stock']}",
            ],
        }

    if action == "show_cart":
        if not db["cart"]:
            return {
                "title": "Cart status",
                "message": "Your cart is empty right now.",
                "items": ["Use the Add to Cart buttons from the dashboard to build an order."],
            }

        items = []
        for item in db["cart"]:
            product = next(
                (product for product in products if product["name"] == item["product"]),
                None,
            )
            price = product["price"] if product else 0
            items.append(
                f"{item['product']} x{item['qty']} = Rs. {price * int(item['qty'])}"
            )

        items.append(f"Total amount: Rs. {summary['total']}")
        return {
            "title": "Cart status",
            "message": f"You currently have {summary['item_count']} item(s) in the cart.",
            "items": items,
        }

    if action == "delivery_help":
        fastest = min(products, key=lambda product: int(product["delivery"].split()[0]))
        return {
            "title": "Delivery help",
            "message": f"{fastest['name']} has the fastest delivery right now.",
            "items": [
                f"Expected delivery: {fastest['delivery']}",
                "Dashboard tip: compare the delivery badges on each product card before adding.",
            ],
        }

    return {
        "title": "Assistant",
        "message": "Choose one of the quick action buttons to explore the store.",
        "items": [],
    }


@app.route("/")
def index():
    db = load()
    return render_template(
        "index.html",
        products=db["products"],
        cart=db["cart"],
        overview=build_overview(db),
        profile={
            "name": "Alena",
            "phone": "9999999999",
            "email": "alena@example.com",
            "orders": 3,
        },
    )


@app.route("/dashboard-data")
def dashboard_data():
    db = load()
    return jsonify(
        {
            "products": db["products"],
            "cart": db["cart"],
            "overview": build_overview(db),
            "cart_summary": build_cart_summary(db),
        }
    )


@app.route("/products")
def products():
    return jsonify(load()["products"])


@app.route("/cart")
def cart():
    return jsonify(load()["cart"])


@app.route("/add", methods=["POST"])
def add():
    data = request.get_json(silent=True) or {}

    if "product" not in data or "qty" not in data:
        return jsonify({"msg": "missing 'product' or 'qty' in request"}), 400

    try:
        qty = int(data["qty"])
        if qty <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"msg": "qty must be a positive integer"}), 400

    db = load()

    for product in db["products"]:
        if product["name"].lower() == str(data["product"]).lower():
            if product["stock"] < qty:
                return jsonify({"msg": "not enough stock"}), 400

            product["stock"] -= qty
            existing = next(
                (
                    item
                    for item in db["cart"]
                    if item["product"].lower() == product["name"].lower()
                ),
                None,
            )

            if existing:
                existing["qty"] += qty
            else:
                db["cart"].append({"product": product["name"], "qty": qty})

            save(db)
            return jsonify(
                {
                    "msg": "added to cart",
                    "cart_summary": build_cart_summary(db),
                    "overview": build_overview(db),
                }
            )

    return jsonify({"msg": "product not found"}), 404


@app.route("/checkout")
def checkout():
    db = load()

    if not db["cart"]:
        return jsonify({"msg": "cart is empty"}), 400

    db["cart"] = []
    save(db)
    return jsonify(
        {
            "msg": "order placed",
            "cart_summary": build_cart_summary(db),
            "overview": build_overview(db),
        }
    )


@app.route("/chatbot", methods=["POST"])
def chatbot():
    payload = request.get_json(silent=True) or {}
    action = payload.get("action", "")
    return jsonify(build_chat_response(action))


if __name__ == "__main__":
    app.run(debug=True)
