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


BOT_STATE = {"product": None, "expecting": None}


def find_product(products, query):
    query = query.lower()
    for product in products:
        if product["name"].lower() in query:
            return product
    return None


def build_chat_response(action="", message=""):
    global BOT_STATE
    db = load()
    products = db["products"]
    summary = build_cart_summary(db)
    overview = build_overview(db)
    action = (action or "").strip().lower()
    message = (message or "").strip().lower()

    if action:
        BOT_STATE["product"] = None
        BOT_STATE["expecting"] = None

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

    if action == "do_checkout":
        if not db["cart"]:
            return {
                "title": "Checkout",
                "message": "Your cart is empty.",
                "items": []
            }
        
        db["cart"] = []
        save(db)
        return {
            "title": "Checkout Successful",
            "message": "Your order has been placed successfully!",
            "items": []
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
                "items": [],
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
        
        BOT_STATE["expecting"] = "delete_confirmation"
        items.append("Would you like to delete a product from the cart? (yes/no)")
        
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
                "Compare the delivery badges on each product card before adding.",
            ],
        }

    if action == "checkout_help":
        return {
            "title": "Checkout help",
            "message": "Add products to the cart and click Checkout Now to place the order.",
            "items": [
                "Step 1: choose a product and quantity",
                "Step 2: click Add To Cart",
                "Step 3: review the cart summary",
                "Step 4: click Checkout Now",
            ],
        }

    if action == "show_offers":
        return {
            "title": "Today's offers",
            "message": "",
            "items": [
                "Laptop: 5% instant discount on card payment",
                "Phone: Free delivery + basic case included",
                "Power Bank: 10% off with any phone purchase",
                "USB-C Cable: Buy 2 for the price of 1",
            ],
        }

    if action == "payment_help":
        return {
            "title": "Payment help",
            "message": "You can complete orders using basic payment options.",
            "items": [
                "Cash on Delivery (COD)",
                "UPI (GPay / PhonePe / Paytm)",
                "Debit/Credit cards",
            ],
        }

    if action == "return_help":
        return {
            "title": "Return and refund",
            "message": "",
            "items": [
                "Return window: within 7 days of delivery",
                "Product should be in original condition",
                "Refund processed in 3 to 5 working days",
            ],
        }

    if action == "contact_help":
        return {
            "title": "Support contact",
            "message": "You can reach support for order or product doubts.",
            "items": [
                "Email: support@ecomdemo.com",
                "Phone: +91 90000 12345",
                "Support time: 9 AM to 6 PM",
            ],
        }

    if action == "show_status":
        return {
            "title": "Store status",
            "message": "Here is the current status.",
            "items": [
                f"Products available: {overview['product_count']}",
                f"Units in stock: {overview['available_units']}",
                f"Items in cart: {overview['cart_items']}",
                f"Cart total: Rs. {overview['cart_total']}",
            ],
        }

    if message:
        if BOT_STATE["expecting"] == "confirmation":
            if message in ["yes", "y", "sure", "ok", "order", "buy"]:
                BOT_STATE["expecting"] = "quantity"
                return {
                    "title": "Quantity",
                    "message": f"How many units of {BOT_STATE['product']} would you like to add?",
                    "items": []
                }
            elif message in ["no", "n", "nope", "cancel"]:
                BOT_STATE["product"] = None
                BOT_STATE["expecting"] = None
                return {
                    "title": "Cancelled",
                    "message": "Order cancelled. How else can I help you?",
                    "items": []
                }
            else:
                BOT_STATE["product"] = None
                BOT_STATE["expecting"] = None

        elif BOT_STATE["expecting"] == "quantity":
            if message.isdigit():
                qty = int(message)
                product_name = BOT_STATE["product"]
                
                if qty <= 0:
                    return {
                        "title": "Invalid Quantity",
                        "message": "Please enter a valid positive number for the quantity.",
                        "items": []
                    }
                    
                target_product = next((p for p in db["products"] if p["name"] == product_name), None)
                if not target_product:
                    BOT_STATE["product"] = None
                    BOT_STATE["expecting"] = None
                    return {"title": "Error", "message": "Product not found.", "items": []}
                    
                if target_product["stock"] < qty:
                    return {
                        "title": "Not Enough Stock",
                        "message": f"Sorry, only {target_product['stock']} units available.",
                        "items": []
                    }
                    
                target_product["stock"] -= qty
                existing = next((item for item in db["cart"] if item["product"] == product_name), None)
                if existing:
                    existing["qty"] += qty
                else:
                    db["cart"].append({"product": product_name, "qty": qty})
                save(db)
                
                BOT_STATE["product"] = None
                BOT_STATE["expecting"] = None
                return {
                    "title": "Success",
                    "message": f"Added {qty} {product_name}(s) to your cart.",
                    "items": ["Type 'show cart' to view your cart.", "Type 'checkout' to place your order."]
                }
            elif message in ["cancel", "no", "abort"]:
                BOT_STATE["product"] = None
                BOT_STATE["expecting"] = None
                return {
                    "title": "Cancelled",
                    "message": "Order cancelled. How else can I help you?",
                    "items": []
                }
            else:
                return {
                    "title": "Invalid Quantity",
                    "message": "Please enter a number for the quantity, or type 'cancel'.",
                    "items": []
                }

        elif BOT_STATE["expecting"] == "delete_confirmation":
            if message in ["yes", "y", "sure", "ok"]:
                BOT_STATE["expecting"] = "delete_product"
                return {
                    "title": "Delete Product",
                    "message": "Which product would you like to delete?",
                    "items": [item["product"] for item in db["cart"]] + ["Or type 'cancel' to go back."]
                }
            elif message in ["no", "n", "nope"]:
                BOT_STATE["expecting"] = None
                return {
                    "title": "Cart",
                    "message": "Okay. Type 'checkout' to place your order.",
                    "items": []
                }
            else:
                BOT_STATE["expecting"] = None

        elif BOT_STATE["expecting"] == "delete_product":
            target = find_product(db["products"], message)
            cart_item = next((item for item in db["cart"] if item["product"].lower() == message.lower() or (target and target["name"].lower() == item["product"].lower())), None)
            
            if cart_item:
                db["cart"].remove(cart_item)
                prod = next((p for p in db["products"] if p["name"] == cart_item["product"]), None)
                if prod:
                    prod["stock"] += cart_item["qty"]
                save(db)
                BOT_STATE["expecting"] = None
                return {
                    "title": "Deleted",
                    "message": f"Removed {cart_item['product']} from your cart.",
                    "items": ["Type 'checkout' to place your order."]
                }
            else:
                if message in ["cancel", "back", "no"]:
                    BOT_STATE["expecting"] = None
                    return {"title": "Cancelled", "message": "Deletion cancelled.", "items": ["Type 'checkout' to place your order."]}
                return {
                    "title": "Not Found",
                    "message": "Product not found in cart. Please type the product name or 'cancel'.",
                    "items": []
                }

        if message in ["show status", "status", "overview"]:
            return build_chat_response(action="show_status")

        if message in ["show products", "products", "catalog"]:
            return build_chat_response(action="show_products")

        if message in ["show cart", "cart"]:
            return build_chat_response(action="show_cart")

        if message in ["cheapest product", "best value", "budget item"]:
            return build_chat_response(action="show_best_value")

        if message in ["delivery help", "delivery", "shipping"]:
            return build_chat_response(action="delivery_help")

        if message in ["checkout help"]:
            return build_chat_response(action="checkout_help")

        if message in ["checkout", "checkout now", "place order"]:
            return build_chat_response(action="do_checkout")

        if message in ["payment options", "payment", "pay"]:
            return build_chat_response(action="payment_help")

        if message in ["return policy", "return", "refund"]:
            return build_chat_response(action="return_help")

        matched_product = find_product(products, message)
        if matched_product:
            if matched_product["stock"] > 0:
                BOT_STATE["product"] = matched_product["name"]
                BOT_STATE["expecting"] = "confirmation"
                prompt_msg = "Would you like to place an order for this? (yes/no)"
            else:
                prompt_msg = "This product is currently out of stock."

            return {
                "title": matched_product["name"],
                "message": f"Here are the current details for {matched_product['name']}. {prompt_msg}",
                "items": [
                    f"Price: Rs. {matched_product['price']}",
                    f"Stock: {matched_product['stock']}",
                    f"Delivery: {matched_product['delivery']}",
                    f"Specs: {matched_product['specs']}",
                ],
            }

        if any(word in message for word in ["status", "overview", "summary"]):
            return build_chat_response(action="show_status")

        if any(word in message for word in ["product", "products", "catalog", "items"]):
            return build_chat_response(action="show_products")

        if any(word in message for word in ["cart", "bag"]):
            return build_chat_response(action="show_cart")

        if any(word in message for word in ["cheap", "cheapest", "budget", "lowest"]):
            return build_chat_response(action="show_best_value")

        if any(word in message for word in ["delivery", "fast", "arrive", "shipping"]):
            return build_chat_response(action="delivery_help")

        if any(word in message for word in ["checkout", "order", "buy", "purchase"]):
            return build_chat_response(action="do_checkout")

        if any(word in message for word in ["offer", "offers", "discount", "deal"]):
            return build_chat_response(action="show_offers")

        if any(word in message for word in ["payment", "pay", "upi", "cod", "card"]):
            return build_chat_response(action="payment_help")

        if any(word in message for word in ["return", "refund", "replace", "replacement"]):
            return build_chat_response(action="return_help")

        if any(word in message for word in ["contact", "support", "help desk", "customer care"]):
            return build_chat_response(action="contact_help")

        return {
            "title": "Assistant",
            "message": "Error!",
            "items": [
                "Try: show status, show products, show cart, payment options.",
                "Or type a product name (e.g. laptop, power bank, smartwatch).",
            ],
        }

    return {
        "title": "Assistant",
        "message": "Choose a quick option or type your doubt.",
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
    message = payload.get("message", "")
    return jsonify(build_chat_response(action=action, message=message))


if __name__ == "__main__":
    app.run(debug=True)
