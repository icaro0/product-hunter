from flask import url_for
from slugify import slugify
from sqlalchemy.exc import IntegrityError
from app import db
import datetime

class Price(db.Model):
    __tablename__ = 'price'
    id = db.Column(db.Integer, primary_key=True)
    buy_date = db.Column(db.DateTime())
    price = db.Column(db.Float())
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    def __init__(self, buy_date, price):
        self.buy_date = buy_date
        self.price = price
    def __repr__(self):
        return f'{self.price}'
    @staticmethod
    def get_by_id(id):
        return User.query.get(id)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.relationship("Price")
    title = db.Column(db.String(256), nullable=False)
    title_slug = db.Column(db.String(256), unique=True, nullable=True)
    def __init__(self,price, title):
        self.price = price
        self.title = title
        self.title_slug = slugify(self.title)

    def __repr__(self):
        return f'<Product {self.title}>'

    def save(self):
        if not self.id:
            db.session.add(self)
        if not self.title_slug:
             self.title_slug = slugify(self.title)

        saved = False
        count = 0
        while not saved:
            try:
                db.session.commit()
                saved = True
            except IntegrityError:
                count += 1
                self.title_slug = f'{slugify(self.title)}-{count}'
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def public_url(self):
        return url_for('producto', slug=self.title_slug)

    @staticmethod
    def get_by_slug(slug):
        return Product.query.filter_by(title_slug=slug).first()
    @staticmethod
    def get_by_id(id):
        return Product.query.filter_by(id=id).first()

    @staticmethod
    def get_all():
        return Product.query.all()