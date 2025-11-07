import unittest
import os
# Disable SocketIO for tests
os.environ['TESTING'] = 'True'

from app import create_app, db
from app.models import User, Book, Rating, Review

class BasicTestCase(unittest.TestCase):
    """Basic test cases for WeBook application"""
    
    def setUp(self):
        """Set up test environment"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up after tests"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_app_exists(self):
        """Test that app is created"""
        self.assertIsNotNone(self.app)
    
    def test_home_page(self):
        """Test home page loads"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_user_registration(self):
        """Test user registration"""
        with self.app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('testpass123')
            db.session.add(user)
            db.session.commit()
            
            found_user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(found_user)
            self.assertEqual(found_user.email, 'test@example.com')
            self.assertTrue(found_user.check_password('testpass123'))
    
    def test_book_creation(self):
        """Test book creation"""
        with self.app.app_context():
            book = Book(
                title='Test Book',
                authors='["Test Author"]',
                description='A test book',
                is_manga=False,
                is_novel=True
            )
            db.session.add(book)
            db.session.commit()
            
            found_book = Book.query.filter_by(title='Test Book').first()
            self.assertIsNotNone(found_book)
            self.assertTrue(found_book.is_novel)
    
    def test_rating_and_average(self):
        """Test rating creation and average calculation"""
        with self.app.app_context():
            # Create user and book
            user = User(username='rater', email='rater@example.com')
            user.set_password('pass123')
            book = Book(title='Rated Book', is_novel=True)
            
            db.session.add(user)
            db.session.add(book)
            db.session.commit()
            
            # Create rating
            rating = Rating(user_id=user.id, book_id=book.id, score=5)
            db.session.add(rating)
            db.session.commit()
            
            # Update book's average rating
            book.update_average_rating()
            db.session.commit()
            
            self.assertEqual(book.average_rating, 5.0)
            self.assertEqual(book.ratings_count, 1)

if __name__ == '__main__':
    unittest.main()
