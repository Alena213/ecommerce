# E-commerce Dashboard Website

This project now runs as a website dashboard instead of a CLI-first flow.

## What changed

- The existing Flask backend still powers products, cart, and checkout.
- A new dashboard homepage is available at `http://127.0.0.1:5000/`.
- Product browsing, cart management, and checkout now happen through buttons and cards.
- A right-side chatbot panel is included with an open button and clickable quick actions.
- The chatbot does not require typing. It shows responses from predefined dashboard-friendly buttons.

## Run the project

1. Install dependencies:

```bash
pip install flask
```

2. Start the website:

```bash
python app.py
```

3. Open this URL in your browser:

```text
http://127.0.0.1:5000/
```

## Website features

- Dashboard hero section with summary cards
- Product cards with quantity selector and add-to-cart button
- Cart summary panel with checkout button
- Profile snapshot section
- Mentor-friendly dashboard shortcuts for common actions
- Right-side chatbot drawer with floating open button

## Available API routes

- `GET /products`
- `GET /cart`
- `POST /add`
- `GET /checkout`
- `GET /dashboard-data`
- `POST /chatbot`

## Notes

- `data.json` stores products and cart data.
- The old `main.py` CLI is still present, but the website in `app.py` is now the main user experience.
