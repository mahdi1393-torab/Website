from models.product_images import ProductImage
from flask import Blueprint, render_template, request, session, redirect, abort, url_for,flash
import config
from models.cart import Cart
from models.product import Product
from extentions import db
from datetime import datetime
from datetime import datetime
import jdatetime
from models.time_submit import StockHistory


app = Blueprint("admin", __name__)


@app.before_request
def before_request():
    if request.endpoint in ["admin.login", "admin.anbar_login"]:
        return

    if request.path.startswith("/admin"):
        if "admin_login" not in session:
            abort(403)

    if request.path.startswith("/anbar"):
        if "anbar_login" not in session:
            abort(403)


@app.route('/admin/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get('username', None)
        password = request.form.get('password', None)

        if username == config.ADMIN_USERNAME and password == config.ADMIN_PASSWORD:
            session['admin_login'] = username
            return redirect("/admin/dashboard")
        else:
            return redirect("/admin/login")

    else:
        return render_template("admin/login.html")

@app.route('/payc/login', methods=["POST", "GET"])
def payc_login():
    if request.method == "POST":
        username = request.form.get('username', None)
        password = request.form.get('password', None)

        if username == config.PAYC_USERNAME and password == config.PAYC_PASSWORD:
            session['payc_login'] = username
            return redirect("/payc/dashboard")
        else:
            return redirect("/payc/login")

    else:
        return render_template("payc/payc_login.html")



@app.route('/anbar/login', methods=["POST", "GET"])
def anbar_login():
    if request.method == "POST":
        username = request.form.get('username', None)
        password = request.form.get('password', None)

        if username == config.ANBAR_USERNAME and password == config.ANBAR_PASSWORD:
            session['anbar_login'] = username
            return redirect("/anbar/dashboard/products")
        else:
            return redirect("/anbar/login")

    else:
        return render_template("anbar/anbar_login.html")



@app.route('/payc/dashboard', methods=["GET", "POST"])
def payc_dashboard():
    products = Product.query.all()
    history = StockHistory.query.order_by(StockHistory.id.desc()).all()
    return render_template(
        "payc/payc_products.html",
        history=history, products=products
    )


@app.route('/anbar/dashboard/products', methods=["GET", "POST"])
def anbar_products():
    if request.method == "GET":
        products = Product.query.all()
        return render_template(
            "anbar/anbar_products.html",
            products=products
        )

    product_id = request.form.get("product_id")
    number = int(request.form.get("number") or 0)

    if not product_id:
        abort(400)

    product = Product.query.get_or_404(product_id)

    # افزایش موجودی
    product.number += number

    # فعال یا غیرفعال بودن محصول
    product.active = 1 if product.number > 0 else 0

    # تاریخ و ساعت شمسی
    now = jdatetime.datetime.fromgregorian(datetime=datetime.now())

    # ثبت تاریخچه ورود کالا
    history = StockHistory(
        product_id=product.id,
        count=number,
        submit_time=now.strftime("%Y/%m/%d %H:%M:%S"),
        action="add"
    )

    db.session.add(history)
    db.session.commit()

    flash("موجودی محصول با موفقیت افزایش یافت.")
    return redirect(url_for("admin.anbar_products"))


@app.route('/anbar/dashboard/products/added')
def anbar_products_added():
    products = Product.query.all()
    history = StockHistory.query.order_by(StockHistory.id.desc()).all()
    return render_template(
        "anbar/anbar_products_added.html",
        history=history,products=products
    )

@app.route('/admin/dashboard', methods=["GET"])
def dashboard():
    carts = Cart.query.filter(Cart.status != "pending").all()
    return render_template("admin/dashboard.html", carts=carts)


@app.route('/admin/dashboard/order/<id>', methods=["GET", "POST"])
def order(id):
    cart = Cart.query.filter(Cart.id == id).first_or_404()

    if request.method == "GET":
        return render_template("admin/order.html", cart=cart)
    else:
        status = request.form.get('status')
        cart.status = status
        db.session.commit()
        flash("وضعیت سفارش با موفقیت تغییر کرد")
        return redirect(url_for('admin.order', id=id))


@app.route('/admin/dashboard/products', methods=["GET", "POST"])
def products():
    if request.method == "GET":
        products = Product.query.all()
        return render_template("admin/products.html", products=products)

    name = request.form.get("name")
    description = request.form.get("description")
    price = request.form.get("price")
    active = 1 if request.form.get("active") else 0
    files = request.files.getlist("cover")

    number = 1 if active else 0

    product = Product(
        name=name,
        description=description,
        price=price,
        active=active,
        number=number
    )

    # اول محصول ذخیره شود تا id بگیرد
    db.session.add(product)
    db.session.commit()

    # ذخیره تصاویر
    for i, file in enumerate(files):

        if file.filename == "":
            continue

        filename = f"{product.id}_{i}.jpg"

        file.save(f"static/cover/{filename}")

        image = ProductImage(
            image=filename,
            product_id=product.id
        )

        db.session.add(image)

    db.session.commit()

    flash("محصول جدید اضافه شد")

    return redirect(url_for("admin.products"))
@app.route('/admin/dashboard/edit-product/<id>', methods=["GET", "POST"])
def edit_product(id):
    product = Product.query.filter(Product.id == id).first_or_404()

    if request.method == "GET":
        return render_template("admin/edit-product.html", product=product)

    import os

    product.name = request.form.get("name")
    product.description = request.form.get("description")
    product.price = request.form.get("price")

    if request.form.get("active"):
        product.active = 1
    else:
        product.active = 0
        product.number = 0

    files = request.files.getlist("cover")

    # اگر عکس جدید انتخاب شده باشد
    if files and files[0].filename != "":

        # حذف عکس‌های قبلی از پوشه
        for img in product.images:
            path = os.path.join("static", "cover", img.image)
            if os.path.exists(path):
                os.remove(path)

        # حذف رکوردهای قبلی
        ProductImage.query.filter_by(product_id=product.id).delete()
        db.session.commit()

        # ذخیره عکس‌های جدید
        for i, file in enumerate(files):
            if file.filename == "":
                continue

            filename = f"{product.id}_{i}.jpg"
            file.save(os.path.join("static", "cover", filename))

            db.session.add(ProductImage(
                image=filename,
                product_id=product.id
            ))

    db.session.commit()

    flash("تغییرات با موفقیت ثبت شد")
    return redirect(url_for("admin.edit_product", id=id))