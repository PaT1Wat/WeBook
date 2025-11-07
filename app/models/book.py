from app import db
from datetime import datetime

class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    google_books_id = db.Column(db.String(100), unique=True, index=True)
    open_library_id = db.Column(db.String(100), index=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    authors = db.Column(db.Text)  # JSON string of authors
    description = db.Column(db.Text)
    categories = db.Column(db.Text)  # JSON string of categories
    publisher = db.Column(db.String(255))
    published_date = db.Column(db.String(50))
    page_count = db.Column(db.Integer)
    language = db.Column(db.String(10))
    isbn = db.Column(db.String(20))
    thumbnail_url = db.Column(db.String(500))
    preview_link = db.Column(db.String(500))
    info_link = db.Column(db.String(500))
    average_rating = db.Column(db.Float, default=0.0)
    ratings_count = db.Column(db.Integer, default=0)
    is_manga = db.Column(db.Boolean, default=False)
    is_novel = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reviews = db.relationship('Review', backref='book', lazy='dynamic', cascade='all, delete-orphan')
    ratings = db.relationship('Rating', backref='book', lazy='dynamic', cascade='all, delete-orphan')
    bookmarks = db.relationship('Bookmark', backref='book', lazy='dynamic', cascade='all, delete-orphan')
    
    def update_average_rating(self):
        """Calculate and update average rating from all user ratings"""
        ratings = self.ratings.all()
        if ratings:
            self.average_rating = sum(r.score for r in ratings) / len(ratings)
            self.ratings_count = len(ratings)
        else:
            self.average_rating = 0.0
            self.ratings_count = 0
    
    def __repr__(self):
        return f'<Book {self.title}>'
