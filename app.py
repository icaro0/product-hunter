# save this as app.py
import os
from flask import Flask, escape, request, render_template, flash, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from ocr import get_parsed_text
from flask_sqlalchemy import SQLAlchemy as sa
from sqlalchemy import select
from sqlalchemy.sql.expression import func
import re
from datetime import datetime
from slugify import slugify


UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "kfANmfeeBz4g7ujL0DlcKScMQHgDwzru"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://argonautadigital:argonautadigital@localhost/mercadona'
db = sa(app)

from models import Price, Product

db.create_all()
db.session.commit()

product_pattern = re.compile(r"(\d{1}) ([A-Z0-9 -_]*) (\d,\d\d)")
two_lines_product_pattern = re.compile(r"(\d{1}) ([A-Z\. ]*)")
price_by_kg = re.compile(r"(\d,\d\d\d) kg (\d,\d\d) €/kg (\d,\d\d)")

def processProducts(lines):
    last_line = None
    for line in lines:
        result = re.match(product_pattern, line)
        t_lines = re.match(two_lines_product_pattern, line)
        p_b_kg = re.match(price_by_kg, line)
        if result is not None:
            search = re.search(product_pattern, line)
            print('Cantidad: {}, Producto: {}, Precio: {}'.format( search.group(1), search.group(2), search.group(3)))
            price = Price(datetime.now(),float(search.group(3).replace(',','.')))
            p = Product.get_by_slug(slugify('{}'.format(search.group(2))))
            if p is not None:
                print('Product exist {}'.format(p.title_slug))
                p.price.append(price)
                p.save()
            else:
                product = Product([price],'{}'.format(search.group(2)))
                product.save()
        elif last_line is not None:
            if p_b_kg is not None:
                product_line = re.search(two_lines_product_pattern, last_line)
                product_price_by_kg = re.search(price_by_kg, line)
                print('Cantidad: {}, Producto: {}, Precio kg: {}, Precio: {}'.format( product_price_by_kg.group(1), product_line.group(2), product_price_by_kg.group(2), product_price_by_kg.group(3)))
            else:
                print('Segunda linea incorrecta en: {} y {}'.format(last_line, line))
            last_line = None
        elif t_lines is not None:
            last_line = line
        else:
            print('No encontre nada en: {}'.format(line))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('resultados',
                                    filename=filename))
    return render_template('index.html')

@app.route('/ocr/<filename>',methods=['GET', 'POST'])
def resultados(filename):
    if request.method == 'POST':
        lines = request.form.getlist('lines[]')
        #procesar imagen aqui
        processProducts(lines)
        flash('Info received')
        return redirect(request.url)
    texto = get_parsed_text('uploads/' + filename)
    return render_template('resultados.html',contenido=texto, filename=filename)

@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/productos')
def productos():
    productos = Product.get_all()
    return render_template('productos.html', productos=productos)

@app.route('/producto/<slug>')
def producto(slug):
    producto = Product.get_by_slug(slug)
    print(producto)
    return render_template('producto.html', producto=producto)