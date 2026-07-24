from flask import Blueprint, render_template, request
from sqlalchemy.sql.expression import func
from sqlalchemy import or_
from models.product import Product
from models.product import Product
from flask import Blueprint, render_template, request



app = Blueprint("general", __name__)

@app.route("/", methods=["GET"])
def main():
    search = request.args.get("search", "").strip()


    if search:
        products = Product.query.filter(
            or_(
                Product.name.contains(search),
                Product.description.contains(search)
            )
        ).all()
    else:
        products = Product.query.filter(Product.active == 1).all()
    return render_template(
        "main.html",
        products=products,
        search=search
    )
@app.route('/product/<int:id>/<name>')
def product(id, name):
    product = Product.query.filter(
        Product.id == id,
        Product.name == name
    ).first_or_404()

    another_products = Product.query.filter(
        Product.name.like(f'%{product.name[:5]}%'),
        Product.id != product.id
    ).order_by(func.random()).limit(3).all()

    return render_template(
        'product.html',
        product=product,
        another_products=another_products
    )

@app.route('/about')
def about():
    return render_template('about.html')
