# ECOM CLI — Test & Run Instructions

## 1. Prerequisites
```
Python 3.8+
pip install flask requests
```

## 2. Start the Backend (Terminal 1)
```bash
cd ecom_cli_phase2
python app.py
# → Running on http://127.0.0.1:5000
```

## 3. Start the CLI (Terminal 2)
```bash
cd ecom_cli_phase2
python main.py
```

---

## 4. Manual Test Checklist

| # | Test | Input | Expected |
|---|------|-------|----------|
| 1 | View products (menu) | `1` | Product list displayed |
| 2 | View products (NLP) | `show products` | Product list displayed |
| 3 | Select by number | `2` at product list | Phone details shown |
| 4 | Select by name | `laptop` at product list | Laptop details shown |
| 5 | Invalid number | `99` at product list | Error, no crash |
| 6 | Add to cart | select → `add` → qty `1` | ADDED TO CART |
| 7 | Invalid qty input | `abc` as quantity | Re-prompted, no crash |
| 8 | Exceed stock | qty > stock | Error: only N units |
| 9 | View cart | `2` or `cart` | Cart + total displayed |
| 10 | Empty cart | `cart` before adding | "Your cart is empty" |
| 11 | Checkout | `checkout` with items | ORDER PLACED |
| 12 | Checkout empty | `checkout` on empty | "cart is empty" |
| 13 | Profile | `3` or `profile` | Name/phone/email shown |
| 14 | Help | `4` or `help` | Commands listed |
| 15 | Exit | `5` or `exit` | Goodbye, quits cleanly |
| 16 | NLP natural | `i want to see products` | product_flow triggered |
| 17 | Server resilience | stop app.py, use CLI | Error message, no crash |

---

## 5. API Quick Test (curl)
```bash
# Get all products
curl http://127.0.0.1:5000/products

# Get cart
curl http://127.0.0.1:5000/cart

# Add to cart
curl -X POST http://127.0.0.1:5000/add \
     -H "Content-Type: application/json" \
     -d '{"product":"Laptop","qty":1}'

# Checkout
curl http://127.0.0.1:5000/checkout
```

---

## 6. Bug Fixes Summary

| # | File | Bug | Fix |
|---|------|-----|-----|
| 1 | app.py | /add crashes on missing body | Added request.json guard + 400 |
| 2 | app.py | Checkout works on empty cart | Empty cart check added |
| 3 | app.py | data.json path fails if CWD wrong | Used absolute __file__ path |
| 4 | main.py | NLP condition always True | Fixed boolean logic |
| 5 | main.py | int(input()) crashes on bad qty | Added isdigit() loop |
| 6 | main.py | IndexError on bad product number | Added bounds check |
| 7 | main.py | No error handling on API calls | Added api_get/api_post helpers |
| 8 | main.py | Cart shows no prices/total | Added price cross-ref + total |
