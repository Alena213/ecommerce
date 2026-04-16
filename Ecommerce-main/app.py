"""
=============================================================================
FILE: app.py
PROJECT: E-Commerce CLI Chatbot (Phase 2)
PURPOSE: Flask-based REST API backend for the e-commerce system.

This module handles all server-side operations:
  - Serving product data
  - Managing shopping cart (add, view)
  - Checkout processing
  - JSON-based persistence (data.json)

USAGE:
  Run this file first before starting main.py:
    $ python app.py

  The server starts at: http://127.0.0.1:5000
=============================================================================
"""

from flask import Flask, jsonify, request
import json
import os

# ============================================================
# APP INITIALIZATION
# ============================================================
# Create a Flask application instance.
# __name__ tells Flask where to look for resources.
app = Flask(__name__)

# ============================================================
# HELPER: Resolve data.json path relative to this file
# ============================================================
# This fix ensures data.json is always found regardless of
# which directory the user launches the script from.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.json")


# ============================================================
# HELPER: load()
# ============================================================
def load():
    """
    Read and parse the JSON data file (data.json).

    Returns:
        dict: The full database containing:
              - "products" (list): all product objects
              - "cart"     (list): current items in cart

    Raises:
        FileNotFoundError: if data.json is missing
        json.JSONDecodeError: if data.json is malformed
    """
    with open(DATA_FILE, "r") as f:
        return json.load(f)


# ============================================================
# HELPER: save(data)
# ============================================================
def save(data):
    """
    Write the given data dictionary back to data.json.

    This is called after any state-mutating operation
    (add to cart, checkout) to persist changes.

    Args:
        data (dict): The full database dict to serialize and save.
    """
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ============================================================
# ROUTE: GET /products
# ============================================================
@app.route('/products')
def products():
    """
    Return all products from the data store.

    Method  : GET
    Endpoint: /products
    Auth    : None

    Returns:
        JSON array of product objects, each with:
          - name     (str)
          - price    (int)
          - stock    (int)
          - delivery (str)
          - specs    (str)

    Example Response:
        [
          {"name": "Laptop", "price": 50000, "stock": 5, ...},
          ...
        ]
    """
    return jsonify(load()["products"])


# ============================================================
# ROUTE: GET /cart
# ============================================================
@app.route('/cart')
def cart():
    """
    Return the current contents of the shopping cart.

    Method  : GET
    Endpoint: /cart
    Auth    : None

    Returns:
        JSON array of cart item objects, each with:
          - product (str): product name
          - qty     (int): quantity added

    Example Response:
        [{"product": "Laptop", "qty": 1}]
    """
    return jsonify(load()["cart"])


# ============================================================
# ROUTE: POST /add
# ============================================================
@app.route('/add', methods=['POST'])
def add():
    """
    Add a product to the cart after validating stock.

    Method  : POST
    Endpoint: /add
    Auth    : None
    Body    : JSON object with:
                - product (str): name of the product to add
                - qty     (int): quantity to add

    Business Logic:
        1. Find the product by name (case-insensitive match).
        2. Check if sufficient stock exists.
        3. Decrement stock and append item to cart.
        4. Persist changes.

    Returns:
        JSON object with key "msg":
          - "added to cart"      → success
          - "not enough stock"   → stock < requested qty
          - "product not found"  → no matching product name
          - "invalid request"    → missing/bad JSON body (BUG FIX)

    Example Request Body:
        {"product": "Laptop", "qty": 2} -> key:value pair in the request body
    """
    # BUG FIX: Guard against missing or non-JSON request body
    # Original code would crash with AttributeError if body was absent.
    if not request.json:
        return jsonify({"msg": "invalid request"}), 400

    data = request.json

    # BUG FIX: Validate required fields exist in the request body.
    if "product" not in data or "qty" not in data:
        return jsonify({"msg": "missing 'product' or 'qty' in request"}), 400

    # BUG FIX: Ensure qty is a positive integer.
    # Original code would allow qty=0 or negative values.
    try:
        qty = int(data["qty"])
        if qty <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"msg": "qty must be a positive integer"}), 400

    db = load()

    for p in db["products"]:
        if p["name"].lower() == data["product"].lower():
            if p["stock"] >= qty:  #5 >= 2
                p["stock"] -= qty  # 5-2 = 3  qty is deducted from stock
                # Store product name and validated qty in cart
                db["cart"].append({"product": p["name"], "qty": qty})
                save(db)
                return jsonify({"msg": "added to cart"})
            return jsonify({"msg": "not enough stock"})

    return jsonify({"msg": "product not found"})


# ============================================================
# ROUTE: GET /checkout
# ============================================================
@app.route('/checkout')
def checkout():
    """
    Process checkout by clearing the cart.

    Method  : GET
    Endpoint: /checkout
    Auth    : None

    Business Logic:
        1. Load current database.
        2. Verify cart is not empty before clearing (BUG FIX).
        3. Reset cart to empty list.
        4. Persist changes.

    Returns:
        JSON object with key "msg":
          - "order placed"    → success
          - "cart is empty"   → nothing to check out (BUG FIX)

    Example Response:
        {"msg": "order placed"}
    """
    db = load()

    # BUG FIX: Original code would silently "checkout" with an empty cart.
    # Now we return a clear message if cart is empty.
    if not db["cart"]:
        return jsonify({"msg": "cart is empty"})

    db["cart"] = []
    save(db)
    return jsonify({"msg": "order placed"})


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == '__main__': # This block ensures the server only starts when this file is run directly.
    app.run(debug=True)
