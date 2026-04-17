import requests


BASE_URL = "http://127.0.0.1:5000"
BANNER = """
====================================
           ECOM CLI
====================================
"""

PROFILE = {
    "name": "Alena",
    "phone": "9999999999",
    "email": "alena@example.com",
    "orders": 3,
}


def section(title):
    line = "=" * 10
    header = f"{title} {line}"
    print(f"\n{header}")
    return len(header)


def section_end(width):
    print("=" * width)


def api_get(path):
    try:
        response = requests.get(f"{BASE_URL}{path}", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        print("\n[ERROR] Server not reachable.")
        return None


def api_post(path, payload):
    try:
        response = requests.post(f"{BASE_URL}{path}", json=payload, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        print("\n[ERROR] Server not reachable.")
        return None


def get_input(prompt):
    while True:
        value = input(prompt).strip().lower()
        if value:
            return value
        print("[ERROR] Input cannot be empty.")


def next_action():
    print("\nWhat next?")
    print("1. Back")
    print("2. Main Menu")
    print("3. Exit")

    while True:
        choice = get_input("Enter: ")
        if choice in ["1", "back"]:
            return "back"
        if choice in ["2", "menu"]:
            return "menu"
        if choice in ["3", "exit"]:
            raise SystemExit
        print("[ERROR] Invalid choice")


def show_menu():
    width = section("MAIN MENU")
    print("1. View Products")
    print("2. View Cart")
    print("3. View Profile")
    print("4. Help")
    print("5. Exit")
    section_end(width)


def product_flow():
    while True:
        products = api_get("/products")
        if not products:
            return

        width = section("PRODUCTS")
        for index, product in enumerate(products, 1):
            print(
                f"{index}. {product['name']} | Rs. {product['price']} | Stock: {product['stock']}"
            )
        section_end(width)

        choice = get_input("\nSelect product (number/name) or 'back': ")
        if choice in ["back", "menu"]:
            return

        selected = None
        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(products):
                selected = products[index]
            else:
                print("[ERROR] Invalid product number.")
                continue
        else:
            matches = [product for product in products if choice in product["name"].lower()]
            if not matches:
                print("[ERROR] No product found.")
                continue
            if len(matches) > 1:
                print("[ERROR] Multiple matches. Be specific.")
                continue
            selected = matches[0]

        while True:
            width = section("PRODUCT DETAILS")
            print(f"Name     : {selected['name']}")
            print(f"Price    : Rs. {selected['price']}")
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

            while True:
                quantity = get_input("Quantity: ")
                if not quantity.isdigit():
                    print("[ERROR] Enter a valid number.")
                    continue

                quantity = int(quantity)
                if quantity <= 0:
                    print("[ERROR] Must be greater than 0.")
                    continue
                if quantity > selected["stock"]:
                    print(f"[ERROR] Only {selected['stock']} available.")
                    continue
                break

            result = api_post("/add", {"product": selected["name"], "qty": quantity})
            if result:
                print(f"\n[OK] {result['msg']}")

            next_action()
            break


def cart_flow():
    while True:
        cart = api_get("/cart")
        if cart is None:
            return
        if not cart:
            print("\nCart is empty")
            return

        products = api_get("/products") or []
        price_map = {product["name"]: product["price"] for product in products}

        width = section("CART")
        total = 0
        for item in cart:
            price = price_map.get(item["product"], 0)
            subtotal = price * item["qty"]
            total += subtotal
            print(f"{item['product']} x{item['qty']} = Rs. {subtotal}")
        print(f"\nTOTAL: Rs. {total}")
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
            print(f"\n[OK] {result['msg']}")
            print("Order placed successfully!")
        next_action()


def profile_flow():
    while True:
        width = section("PROFILE")
        for key, value in PROFILE.items():
            print(f"{key.capitalize():<10}: {value}")
        section_end(width)

        choice = next_action()
        if choice in ["back", "menu"]:
            return


def help_flow():
    while True:
        width = section("HELP")
        print("show / 1 -> products")
        print("cart / 2 -> cart")
        print("profile / 3 -> profile")
        print("exit / 5 -> exit")
        print("back -> go back")
        section_end(width)

        choice = next_action()
        if choice in ["back", "menu"]:
            return


def main():
    print(BANNER)

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
