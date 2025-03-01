from app import db
from datetime import datetime
import logging
from sqlalchemy.exc import SQLAlchemyError
from app.models.user import User


# Setting up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserBehavior(db.Model):
    """
    Model to track user interactions with products.
    """
    __tablename__ = 'user_behavior'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)  # e.g., view, add_to_cart, purchase
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Default to current UTC time

    # Relationships
    user = db.relationship('User')  # Removed the backref
    product = db.relationship('Product', backref='behaviors')  # Kept the backref here for Product

    # Optional: Index on user_id and product_id for faster queries
    __table_args__ = (
        db.Index('ix_user_product', 'user_id', 'product_id'),
    )

    def __repr__(self):
        return f"<UserBehavior user_id={self.user_id} product_id={self.product_id} action={self.action_type} timestamp={self.timestamp}>"

def get_user_behavior(user_id):
    """
    Fetch all user behavior records for a given user ID.

    :param user_id: ID of the user
    :return: List of UserBehavior records or an empty list if none found
    """
    try:
        user_behavior = UserBehavior.query.filter_by(user_id=user_id).all()
        if not user_behavior:
            logger.info(f"No behavior data found for user with ID {user_id}. Returning an empty list.")
            return []  # Return an empty list if no data found
        return user_behavior
    except SQLAlchemyError as e:
        logger.error(f"Error while fetching user behavior for user with ID {user_id}: {str(e)}")
        return []  # Return an empty list if there was an error
