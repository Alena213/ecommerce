import requests

BASE = "http://127.0.0.1:5000"

banner = r'''{line} 
 ███████╗ ██████╗ ██████╗ ███╗   ███╗
 ██╔════╝██╔════╝██╔═══██╗████╗ ████║
 █████╗  ██║     ██║   ██║██╔████╔██║
 ██╔══╝  ██║     ██║   ██║██║╚██╔╝██║
 ███████╗╚██████╗╚██████╔╝██║ ╚═╝ ██║
 ╚══════╝ ╚═════╝ ╚═════╝ ╚═╝     ╚═╝

            ECOM CLI
====================================
'''

# ============================================================
# UI HELPERS
# ============================================================
def section(title):
    line = "=" * 10
    header = f"{title} {line}"
    print(f"\n{header}")
    return len(header)


def section_end(width):
    print("=" * width)


# ============================================================
# API HELPERS
# ============================================================
def api_get(path):#    http://127.0.0.1:5000/products
    try:
        res = requests.get(BASE + path, timeout=5)
        res.raise_for_status()#400 200
        return res.json()
    except:
        print("\n[ERROR] Server not reachable.")
        return None



def api_post(path, payload):
    try:
        res = requests.post(BASE + path, json=payload, timeout=5)
        res.raise_for_status()
        return res.json()
    except:
        print("\n[ERROR] Server not reachable.")
        return None


# ============================================================
# INPUT VALIDATION (CORE FIX)
# ============================================================
def get_input(prompt):
    """
    Forces non-empty input.
    Prevents accidental Enter bugs.
    """
    while True:
        value = input(prompt).strip().lower()
        if value == "":
            print("[ERROR] Input cannot be empty.")
            continue
        return value


# ============================================================
# NAVIGATION
# ============================================================
def next_action():
    print("\nWhat next?")
    print("1. Back")
    print("2. Main Menu")
    print("3. Exit")

    while True:
        choice = get_input("Enter: ")

        if choice in ["1", "back"]:
            return "back"
        elif choice in ["2", "menu"]:
            return "menu"
        elif choice in ["3", "exit"]:
            exit()
        else:
            print("[ERROR] Invalid choice")


# ============================================================
# MENU
# ============================================================
def show_menu():
    width = section("MAIN MENU")

    print("1. View Products")
    print("2. View Cart")
    print("3. View Profile")
    print("4. Help")
    print("5. Exit")

    section_end(width)


# ============================================================
# PRODUCT FLOW (FULLY FIXED)
# ============================================================
def product_flow():
    while True:
        products = api_get("/products")
        if not products:
            return

        width = section("PRODUCTS")

        for i, p in enumerate(products, 1):
            print(f"{i}. {p['name']} | ₹{p['price']} | Stock: {p['stock']}")

        section_end(width)

        choice = get_input("\nSelect product (number/name) or 'back': ")

        if choice in ["back", "menu"]:
            return

        selected = None

        # ---- NUMBER ----
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(products):
                selected = products[idx]
            else:
                print("[ERROR] Invalid product number.")
                continue

        # ---- NAME ----
        else:
            matches = [p for p in products if choice in p["name"].lower()]

            if len(matches) == 0:
                print("[ERROR] No product found.")
                continue

            if len(matches) > 1:
                print("[ERROR] Multiple matches. Be specific.")
                continue

            selected = matches[0]

        # =========================
        # DETAILS LOOP
        # =========================
        while True:
            width = section("PRODUCT DETAILS")

            print(f"Name     : {selected['name']}")
            print(f"Price    : ₹{selected['price']}")
            print(f"Stock    : {selected['stock']}")
            print(f"Specs    : {selected.get('specs')}")

            section_end(width)

            if selected["stock"] == 0:
                print("Out of stock")
                break

            action = get_input("Type 'add' or 'back': ")

            if action == "back":
                break

            if action != "add":
                print("[ERROR] Invalid action.")
                continue

            # ---- QUANTITY ----
            while True:
                qty = get_input("Quantity: ")

                if not qty.isdigit():
                    print("[ERROR] Enter a valid number.")
                    continue

                qty = int(qty)

                if qty <= 0:
                    print("[ERROR] Must be > 0.")
                    continue

                if qty > selected["stock"]:
                    print(f"[ERROR] Only {selected['stock']} available.")
                    continue

                break

            result = api_post("/add", {
                "product": selected["name"],
                "qty": qty
            })

            if result:
                print(f"\n✓ {result['msg']}")

            next_action()
            break


# ============================================================
# CART FLOW (SAFE)
# ============================================================
def cart_flow():
    while True:
        cart = api_get("/cart")
        if cart is None:
            return

        if not cart:
            print("\nCart is empty")
            return

        products = api_get("/products") or []
        price_map = {p["name"]: p["price"] for p in products}

        width = section("CART")

        total = 0
        for item in cart:
            price = price_map.get(item["product"], 0)
            subtotal = price * item["qty"]
            total += subtotal
            print(f"{item['product']} x{item['qty']} = ₹{subtotal}")

        print(f"\nTOTAL: ₹{total}")

        section_end(width)

        action = get_input("\nType 'checkout' or 'back': ")

        if action == "back":
            return

        if action != "checkout":
            print("[ERROR] Invalid action.")
            continue

        confirm = get_input("Confirm order? (yes/no): ")

        if confirm != "yes":
            print("Order cancelled")
            continue

        result = api_get("/checkout")

        if result:
            print(f"\n✓ {result['msg']}")
            print("Order placed successfully!")

        next_action()


# ============================================================
# PROFILE
# ============================================================
def profile_flow():
    while True:
        profile = {
            "name": "Alena",
            "phone": "9999999999",
            "email": "alena@example.com",
            "orders": 3
        }

        width = section("PROFILE")

        for k, v in profile.items():
            print(f"{k.capitalize():<10}: {v}")

        section_end(width)

        choice = next_action()

        if choice in ["back", "menu"]:
            return


# ============================================================
# HELP
# ============================================================
def help_flow():
    while True:
        width = section("HELP")

        print("show / 1 → products")
        print("cart / 2 → cart")
        print("profile / 3 → profile")
        print("exit / 5 → exit")
        print("back → go back")

        section_end(width)

        choice = next_action()

        if choice in ["back", "menu"]:
            return


# ============================================================
# MAIN
# ============================================================
def main():
    print(banner)

    while True:
        show_menu()
        user = get_input("\nEnter: ")

        if user == "1" or "product" in user or "show" in user:
            product_flow()

        elif user == "2" or "cart" in user:
            cart_flow()

        elif user == "3" or "profile" in user:
            profile_flow()

        elif user == "4" or "help" in user:
            help_flow()

        elif user == "5" or "exit" in user:
            print("Goodbye!")
            break

        else:
            print("[ERROR] Invalid input")


if __name__ == "__main__":
    main()