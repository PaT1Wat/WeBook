from app import db
from datetime import datetime

class Bookmark(db.Model):
    __tablename__ = 'bookmarks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False, index=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'book_id', name='unique_user_book_bookmark'),)
    
    def __repr__(self):
        return f'<Bookmark User {self.user_id} - Book {self.book_id}>'
