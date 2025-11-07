# WeBook Quick Start Guide

## Getting Started in 5 Minutes

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/PaT1Wat/WeBook.git
cd WeBook

# Run the startup script (Unix/Linux/Mac)
./start.sh

# OR manually:
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Start the application
python run.py
```

### 2. Access the Application

Open your browser and navigate to:
```
http://localhost:5000
```

### 3. Create Your First Account

1. Click "Register" in the navigation bar
2. Fill in your username, email, and password
3. Click "Register" to create your account
4. You'll be redirected to login

### 4. Explore Books

1. **Search for Books**: Click "Search" and enter a book title or author
2. **Import Books**: From search results, click "Import Book" to add to database
3. **Browse Books**: Click "Browse" to see all imported books
4. **View Details**: Click on any book to see full details

### 5. Rate and Review

1. Go to any book detail page
2. Click on stars to rate (1-5 stars)
3. Click "Write Review" to add your thoughts
4. Your ratings help improve recommendations!

### 6. Get Recommendations

1. Click "For You" in the navigation (after rating a few books)
2. View personalized recommendations based on your taste
3. Click "Popular" to see trending books

### 7. Join the Community

1. **Forum**: Click "Forum" to read and create discussion posts
2. **Chat**: Click "Chat" to join real-time conversations
3. **Categories**: Switch between General, Manga, and Novel rooms

### 8. Bookmark Your Favorites

1. On any book page, click "Bookmark"
2. Add personal notes if desired
3. Access all bookmarks from "Bookmarks" in navigation

## Admin Features

### Create an Admin User

Run this Python script:

```python
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    admin = User(username='admin', email='admin@webook.com')
    admin.set_password('admin123')  # Change this password!
    admin.is_admin = True
    db.session.add(admin)
    db.session.commit()
    print("Admin user created!")
```

### Admin Dashboard

1. Login as admin user
2. Click "Admin" in navigation
3. Access:
   - User management
   - Book management
   - Forum moderation
   - Analytics dashboard
   - Recommendation system training

## Tips for Best Experience

1. **Rate Multiple Books**: The more you rate, the better your recommendations
2. **Try Both APIs**: Search with both Google Books and Open Library for more results
3. **Join Discussions**: Engage with community in forum and chat
4. **Mark Manga/Novels**: When importing, books are auto-categorized based on metadata
5. **Train Recommender**: Admins should train the ML model after significant new data

## API Usage

### Example: Search Books via API

```bash
# Search Google Books
curl "http://localhost:5000/books/search?q=naruto&source=google"

# Search Open Library
curl "http://localhost:5000/books/search?q=harry+potter&source=openlibrary"
```

### Example: Get Recommendations

```bash
# Get personalized recommendations (requires authentication)
curl -H "Content-Type: application/json" \
     http://localhost:5000/recommendations/for-you

# Get popular books
curl http://localhost:5000/recommendations/popular
```

## Troubleshooting

### Database Issues
```bash
# Delete and recreate database
rm webook.db
python run.py  # Will auto-create new database
```

### Port Already in Use
```bash
# Find and kill process using port 5000
lsof -ti:5000 | xargs kill -9
```

### Module Not Found Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Next Steps

- Configure Google Books API key for unlimited searches
- Customize the theme in `app/static/css/style.css`
- Add more book categories
- Implement email notifications
- Deploy to production server

## Support

For issues or questions:
- Check the main [README.md](README.md)
- Open an issue on GitHub
- Join our community forum (in the app!)

Happy Reading! 📚
