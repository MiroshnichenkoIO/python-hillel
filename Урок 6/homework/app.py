"""Інтернет-магазин на Flask: каталог, товар, замовлення."""

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

PRODUCTS: list[dict] = [
    {"id": 1, "title": "Клавіатура Keychron", "price": 3450.0},
    {"id": 2, "title": "Миша Logitech", "price": 4100.0},
    {"id": 3, "title": "Навушники Sony", "price": 12300.0},
    {"id": 4, "title": "Веб-камера Logitech", "price": 1150.0},
]

ORDERS: list[dict] = []


def find_product(product_id: int) -> dict | None:
    """Повертає товар за номером або None."""
    for product in PRODUCTS:
        if product["id"] == product_id:
            return product
    return None


@app.get("/")
def catalog() -> str:
    """Показує каталог товарів."""
    return render_template("catalog.html", products=PRODUCTS)


@app.get("/product/<int:product_id>")
def product_page(product_id: int) -> str:
    """Показує картку товару з формою замовлення."""
    product = find_product(product_id)
    if product is None:
        return render_template("catalog.html", products=PRODUCTS, message="Такого товару немає")
    return render_template("product.html", product=product)


@app.post("/order")
def make_order():
    """Приймає форму і зберігає замовлення."""
    product = find_product(int(request.form["product_id"]))
    customer = request.form.get("customer", "").strip()
    if product and customer:
        ORDERS.append({"customer": customer, "title": product["title"], "price": product["price"]})
    return redirect(url_for("orders_page"))


@app.get("/orders")
def orders_page() -> str:
    """Показує список замовлень."""
    return render_template("orders.html", orders=ORDERS)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
