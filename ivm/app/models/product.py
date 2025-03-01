from app import db
from datetime import datetime

class Product(db.Model):
    """
    Model for products in the store.
    """
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    image_filename = db.Column(db.String(100), nullable=True)  # Store the image filename
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp for when the product was created
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Timestamp for when the product is updated

    # Optional: Adding an index on the name and category columns for faster searches
    __table_args__ = (
        db.Index('ix_product_name_category', 'name', 'category'),
    )

    def __repr__(self):
        return f"<Product {self.name} (Category: {self.category}, Price: {self.price})>"

    def save_image(self, filename):
        """
        A helper method to update the product's image filename.
        """
        self.image_filename = filename
        db.session.commit()

    def get_image_url(self):
        """
        Returns the full URL for the product's image file.
        """
        return f"/static/uploads/{self.image_filename}" if self.image_filename else None

