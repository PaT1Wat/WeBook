# WeBook - Manga & Novel Recommendation System

WeBook is a comprehensive online community platform for manga and novel readers, featuring a hybrid recommendation system powered by Machine Learning that combines Content-Based and Collaborative Filtering algorithms.

## Features

### 🤖 Smart Recommendation System
- **Hybrid Filtering**: Combines Content-Based and Collaborative Filtering
- **Machine Learning**: Uses scikit-learn for analyzing user behavior patterns
- **Personalized Suggestions**: Tailored book recommendations for each user
- **Similar Books**: Content-based recommendations for discovering similar titles

### 📚 Book Management
- **Multi-Source Integration**: Fetches data from Google Books API and Open Library API
- **Search Functionality**: Search across multiple book databases
- **Book Import**: Import books from external APIs into local database
- **Categories**: Organized by manga and novel categories
- **Bookmarks**: Save favorite books with personal notes

### ⭐ Reviews & Ratings
- **User Reviews**: Write detailed reviews with titles and content
- **5-Star Rating System**: Rate books on a scale of 1-5
- **Average Ratings**: Automatically calculated from all user ratings
- **Review Management**: Edit and delete your own reviews

### 💬 Community Features
- **Real-time Chat**: WebSocket-based chat rooms for different topics (General, Manga, Novel)
- **Forum/Bulletin Board**: 
  - Create discussion posts
  - Comment on posts
  - Categories for organization
  - Pin and lock posts (Admin)
- **User Profiles**: Track activity and contributions

### 👨‍💼 Admin Panel
- **User Management**: View all users, toggle admin status
- **Content Moderation**: Manage books, reviews, and forum posts
- **Analytics Dashboard**: View platform statistics
- **Forum Moderation**: Pin, lock, or delete posts

## Technology Stack

### Backend
- **Flask**: Web framework
- **SQLAlchemy**: ORM for database management
- **Flask-Login**: User authentication
- **Flask-SocketIO**: Real-time WebSocket communication
- **SQLite**: Database (easily replaceable with PostgreSQL/MySQL)

### Machine Learning
- **scikit-learn**: ML algorithms and models
- **numpy & pandas**: Data processing
- **TfidfVectorizer**: Content-based text analysis
- **KNN**: Collaborative filtering

### Frontend
- **HTML5/CSS3**: Modern responsive design
- **JavaScript**: Interactive features
- **Socket.IO**: Real-time chat functionality

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/PaT1Wat/WeBook.git
   cd WeBook
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

5. **Initialize the database**
   ```bash
   python run.py
   # The database will be created automatically on first run
   ```

6. **Create an admin user** (optional)
   ```python
   from app import create_app, db
   from app.models import User
   
   app = create_app()
   with app.app_context():
       admin = User(username='admin', email='admin@webook.com')
       admin.set_password('admin123')
       admin.is_admin = True
       db.session.add(admin)
       db.session.commit()
   ```

7. **Run the application**
   ```bash
   python run.py
   ```

8. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## Configuration

### Environment Variables (.env)

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URI=sqlite:///webook.db
GOOGLE_BOOKS_API_KEY=your-google-books-api-key
```

### Google Books API Key

To get a Google Books API key:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Google Books API
4. Create credentials (API Key)
5. Add the key to your `.env` file

Note: The application works without the API key, but with rate limits.

## Usage

### For Users

1. **Register an account** at `/auth/register`
2. **Search for books** using the search page
3. **Import books** from Google Books or Open Library
4. **Rate and review** books you've read
5. **Bookmark** books you want to read
6. **Get recommendations** based on your reading history
7. **Join the community** via forum and chat

### For Admins

1. **Access admin dashboard** at `/admin`
2. **Manage users** - promote to admin, delete users
3. **Moderate content** - manage books, reviews, posts
4. **View statistics** - track platform growth
5. **Train recommendation system** - `/recommendations/train`

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `GET /auth/logout` - User logout
- `GET /auth/profile` - View user profile

### Books
- `GET /books` - List all books
- `GET /books/search?q=query` - Search books
- `GET /books/<id>` - Get book details
- `POST /books/import` - Import book from API
- `POST /books/<id>/bookmark` - Add bookmark
- `DELETE /books/<id>/bookmark` - Remove bookmark

### Reviews & Ratings
- `GET /books/<id>/reviews` - Get book reviews
- `POST /books/<id>/reviews` - Create review
- `PUT /reviews/<id>` - Update review
- `DELETE /reviews/<id>` - Delete review
- `POST /books/<id>/rating` - Rate book

### Recommendations
- `GET /recommendations/for-you` - Personalized recommendations
- `GET /recommendations/similar/<id>` - Similar books
- `GET /recommendations/popular` - Popular books
- `POST /recommendations/train` - Train ML model (Admin)

### Forum
- `GET /forum` - List forum posts
- `POST /forum/posts` - Create post
- `GET /forum/posts/<id>` - Get post with comments
- `POST /forum/posts/<id>/comments` - Add comment

### Chat
- `GET /chat` - Chat interface
- `GET /chat/messages/<room>` - Get chat history

## Project Structure

```
WeBook/
├── app/
│   ├── __init__.py              # Flask app initialization
│   ├── models/                  # Database models
│   │   ├── user.py
│   │   ├── book.py
│   │   ├── review.py
│   │   ├── rating.py
│   │   ├── bookmark.py
│   │   ├── forum.py
│   │   └── chat.py
│   ├── routes/                  # Route handlers
│   │   ├── auth.py
│   │   ├── books.py
│   │   ├── reviews.py
│   │   ├── forum.py
│   │   ├── chat.py
│   │   ├── admin.py
│   │   └── recommendations.py
│   ├── ml/                      # Machine Learning
│   │   └── recommender.py       # Hybrid recommendation system
│   ├── utils/                   # Utility functions
│   │   └── api_client.py        # External API clients
│   ├── static/                  # Static files
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── templates/               # HTML templates
│       ├── base.html
│       ├── index.html
│       ├── auth/
│       ├── books/
│       ├── reviews/
│       ├── forum/
│       ├── chat/
│       ├── admin/
│       └── recommendations/
├── tests/                       # Unit tests
├── data/                        # Data files
├── requirements.txt             # Python dependencies
├── run.py                       # Application entry point
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## Machine Learning Algorithm

### Hybrid Recommendation System

The recommendation system combines two approaches:

1. **Content-Based Filtering**
   - Uses TF-IDF vectorization on book metadata (title, authors, categories, description)
   - Calculates cosine similarity between books
   - Recommends books similar to what user has rated highly

2. **Collaborative Filtering**
   - Uses K-Nearest Neighbors (KNN) algorithm
   - Analyzes rating patterns across users
   - Recommends books liked by similar users

3. **Hybrid Approach**
   - Combines both methods with configurable weights
   - Default: 50% content-based, 50% collaborative
   - Provides more accurate and diverse recommendations

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source and available under the MIT License.

## Contact

For questions or support, please open an issue on GitHub.

## Acknowledgments

- Google Books API for book data
- Open Library API for additional book information
- scikit-learn for machine learning algorithms
- Flask community for excellent documentation