# E-commerce Dashboard

This project is a small e-commerce application with:

- a Flask backend
- a dashboard-style website
- an optional CLI client for the original command-based flow

## Project structure

- `app.py`: Flask app and API routes
- `templates/index.html`: dashboard markup
- `static/styles.css`: dashboard styling
- `static/app.js`: dashboard interactivity
- `data.json`: sample product and cart data
- `main.py`: optional CLI client

## Run the website

1. Open the project folder in VS Code:
   `C:\Users\ALENA\Downloads\Ecommerce-main`
2. Open a terminal in VS Code.
3. Run:

```powershell
.\ecom_env\Scripts\python.exe app.py
```

4. Open:
   [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

If your virtual environment is already activated, this also works:

```powershell
python app.py
```

## Run the CLI version

Start the Flask app first, then in another terminal run:

```powershell
python main.py
```

## Dashboard features

- product cards with quantity selection
- cart summary with checkout
- profile snapshot
- quick dashboard actions
- right-side chatbot drawer with clickable prompts

## API routes

- `GET /`
- `GET /products`
- `GET /cart`
- `POST /add`
- `GET /checkout`
- `GET /dashboard-data`
- `POST /chatbot`

## Notes

- The main user experience is the website in `app.py`.
- `data.json` can be reset any time if you want a clean sample cart.
