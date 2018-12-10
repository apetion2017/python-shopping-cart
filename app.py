from flask import *
import sqlite3, os

app = Flask(__name__)
app.secret_key = 'random string'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/")
def root():
    with sqlite3.connect('db.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products')
        itemData = cur.fetchall()
        cur.execute('SELECT categoryId, name FROM categories')
        categoryData = cur.fetchall()
    itemData = parse(itemData)
    return render_template('home.html', itemData=itemData, categoryData=categoryData)


@app.route("/add")
def admin():
    with sqlite3.connect('db.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT categoryId, name FROM categories")
        categories = cur.fetchall()
    conn.close()
    return render_template('add.html', categories=categories)


@app.route("/addItem", methods=["GET", "POST"])
def addItem():
    if request.method == "POST":
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        stock = int(request.form['stock'])
        categoryId = int(request.form['category'])

        #Uploading image procedure
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        imagename = filename
        with sqlite3.connect('db.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute('''INSERT INTO products (name, price, description, image, stock, categoryId) VALUES (?, ?, ?, ?, ?, ?)''', (name, price, description, imagename, stock, categoryId))
                conn.commit()
                msg="added successfully"
            except:
                msg="error occured"
                conn.rollback()
        conn.close()
        print(msg)
        return redirect(url_for('root'))


@app.route("/remove")
def remove():
    with sqlite3.connect('db.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products')
        data = cur.fetchall()
    conn.close()
    return render_template('remove.html', data=data)


@app.route("/removeItem")
def removeItem():
    productId = request.args.get('productId')
    with sqlite3.connect('db.db') as conn:
        try:
            cur = conn.cursor()
            cur.execute('DELETE FROM products WHERE productID = ?', (productId, ))
            conn.commit()
            msg = "Deleted successsfully"
        except:
            conn.rollback()
            msg = "Error occured"
    conn.close()
    print(msg)
    return redirect(url_for('root'))


@app.route("/displayCategory")
def displayCategory():

        categoryId = request.args.get("categoryId")
        with sqlite3.connect('db.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT products.productId, products.name, products.price, products.image, categories.name FROM products, categories WHERE products.categoryId = categories.categoryId AND categories.categoryId = ?", (categoryId, ))
            data = cur.fetchall()
        conn.close()
        categoryName = data[0][4]
        data = parse(data)
        return render_template('displayCategory.html', data=data,  categoryName=categoryName)


@app.route("/productDescription")
def productDescription():
    productId = request.args.get('productId')
    with sqlite3.connect('db.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products WHERE productId = ?', (productId, ))
        productData = cur.fetchone()
    conn.close()
    return render_template("productDescription.html", data=productData)


@app.route("/addToCart")
def addToCart():

        productId = int(request.args.get('productId'))
        with sqlite3.connect('db.db') as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO kart (productId) VALUES (?)", (productId,))
            conn.commit()
            msg = "Added successfully"

        conn.close()
        return redirect(url_for('root'))


@app.route("/cart")
def cart():
    with sqlite3.connect('db.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT products.productId, products.name, products.price, products.image FROM products, kart WHERE products.productId = kart.productId", ())
        products = cur.fetchall()
    totalPrice = 0
    for row in products:
        totalPrice += row[2]
    return render_template("cart.html", products = products, totalPrice=totalPrice)


@app.route("/removeFromCart")
def removeFromCart():
    # if 'email' not in session:
    #     return redirect(url_for('loginForm'))
    # email = session['email']
    productId = int(request.args.get('productId'))
    with sqlite3.connect('db.db') as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM kart WHERE productId = ?", (productId,))
        conn.commit()
        msg = "removed successfully"
    conn.close()
    return redirect(url_for('root'))


def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def parse(data):
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans


if __name__ == '__main__':
    app.run(debug=True)
