from app import db

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(150), nullable=False, default="Uncategorized")
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))
    image_filename = db.Column(db.String(255))  # Store the image filename

    def __repr__(self):
        return f"<Product {self.name}>"
