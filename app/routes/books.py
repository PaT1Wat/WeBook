from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from app import db
from app.models import Book, Bookmark, Rating
from app.utils import GoogleBooksAPI, OpenLibraryAPI
import json

bp = Blueprint('books', __name__)

google_books = GoogleBooksAPI()
open_library = OpenLibraryAPI()

@bp.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@bp.route('/books/search')
def search():
    """Search for books"""
    query = request.args.get('q', '')
    source = request.args.get('source', 'google')  # google or openlibrary
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    if not query:
        if request.is_json:
            return jsonify({'error': 'Search query is required'}), 400
        return render_template('books/search.html', books=[], query='')
    
    start_index = (page - 1) * per_page
    
    if source == 'google':
        results = google_books.search(query, max_results=per_page, start_index=start_index)
        books = [google_books.parse_book_data(item) for item in results.get('items', [])]
    else:
        results = open_library.search(query, limit=per_page, offset=start_index)
        books = [open_library.parse_book_data(doc) for doc in results.get('docs', [])]
    
    if request.is_json:
        return jsonify({'books': books, 'query': query}), 200
    
    return render_template('books/search.html', books=books, query=query)

@bp.route('/books/<int:book_id>')
def book_detail(book_id):
    """Get detailed information about a book"""
    book = Book.query.get_or_404(book_id)
    
    # Parse JSON fields
    authors = json.loads(book.authors) if book.authors else []
    categories = json.loads(book.categories) if book.categories else []
    
    # Check if user has bookmarked this book
    is_bookmarked = False
    user_rating = None
    
    if current_user.is_authenticated:
        is_bookmarked = Bookmark.query.filter_by(
            user_id=current_user.id,
            book_id=book_id
        ).first() is not None
        
        rating = Rating.query.filter_by(
            user_id=current_user.id,
            book_id=book_id
        ).first()
        
        if rating:
            user_rating = rating.score
    
    if request.is_json:
        return jsonify({
            'id': book.id,
            'title': book.title,
            'authors': authors,
            'description': book.description,
            'categories': categories,
            'publisher': book.publisher,
            'published_date': book.published_date,
            'page_count': book.page_count,
            'language': book.language,
            'isbn': book.isbn,
            'thumbnail_url': book.thumbnail_url,
            'average_rating': book.average_rating,
            'ratings_count': book.ratings_count,
            'is_manga': book.is_manga,
            'is_novel': book.is_novel,
            'is_bookmarked': is_bookmarked,
            'user_rating': user_rating
        }), 200
    
    return render_template('books/detail.html', book=book, authors=authors, 
                          categories=categories, is_bookmarked=is_bookmarked,
                          user_rating=user_rating)

@bp.route('/books/import', methods=['POST'])
@login_required
def import_book():
    """Import a book from external API to database"""
    data = request.get_json() if request.is_json else request.form
    
    source = data.get('source', 'google')
    book_id = data.get('book_id')
    
    if not book_id:
        return jsonify({'error': 'Book ID is required'}), 400
    
    # Check if book already exists
    if source == 'google':
        existing_book = Book.query.filter_by(google_books_id=book_id).first()
    else:
        existing_book = Book.query.filter_by(open_library_id=book_id).first()
    
    if existing_book:
        return jsonify({'message': 'Book already in database', 'book_id': existing_book.id}), 200
    
    # Fetch book data
    if source == 'google':
        book_data_raw = google_books.get_book(book_id)
        if not book_data_raw:
            return jsonify({'error': 'Book not found'}), 404
        book_data = google_books.parse_book_data(book_data_raw)
    else:
        book_data_raw = open_library.get_book(book_id)
        if not book_data_raw:
            return jsonify({'error': 'Book not found'}), 404
        # For Open Library, we need to search to get full data
        search_results = open_library.search(book_data_raw.get('title', ''), limit=1)
        if search_results.get('docs'):
            book_data = open_library.parse_book_data(search_results['docs'][0])
        else:
            return jsonify({'error': 'Book data incomplete'}), 404
    
    # Determine if it's manga or novel based on categories
    # Book categorization keywords
    MANGA_KEYWORDS = ['manga', 'comic', 'graphic novel', 'manhwa', 'manhua']
    NOVEL_KEYWORDS = ['novel', 'fiction', 'literature', 'story', 'tale']
    
    categories = json.loads(book_data.get('categories', '[]'))
    categories_lower = [cat.lower() for cat in categories]
    is_manga = any(keyword in cat for cat in categories_lower for keyword in MANGA_KEYWORDS)
    is_novel = any(keyword in cat for cat in categories_lower for keyword in NOVEL_KEYWORDS)
    
    # Create new book
    book = Book(
        google_books_id=book_data.get('google_books_id'),
        open_library_id=book_data.get('open_library_id'),
        title=book_data['title'],
        authors=book_data.get('authors'),
        description=book_data.get('description'),
        categories=book_data.get('categories'),
        publisher=book_data.get('publisher'),
        published_date=book_data.get('published_date'),
        page_count=book_data.get('page_count'),
        language=book_data.get('language'),
        isbn=book_data.get('isbn'),
        thumbnail_url=book_data.get('thumbnail_url'),
        preview_link=book_data.get('preview_link'),
        info_link=book_data.get('info_link'),
        average_rating=book_data.get('average_rating', 0.0),
        ratings_count=book_data.get('ratings_count', 0),
        is_manga=is_manga,
        is_novel=is_novel
    )
    
    db.session.add(book)
    db.session.commit()
    
    return jsonify({'message': 'Book imported successfully', 'book_id': book.id}), 201

@bp.route('/books')
def list_books():
    """List all books in database"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    category = request.args.get('category')
    is_manga = request.args.get('is_manga')
    is_novel = request.args.get('is_novel')
    
    query = Book.query
    
    if category:
        query = query.filter(Book.categories.contains(category))
    if is_manga is not None:
        query = query.filter_by(is_manga=is_manga.lower() == 'true')
    if is_novel is not None:
        query = query.filter_by(is_novel=is_novel.lower() == 'true')
    
    pagination = query.order_by(Book.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    books = pagination.items
    
    if request.is_json:
        return jsonify({
            'books': [{
                'id': b.id,
                'title': b.title,
                'authors': json.loads(b.authors) if b.authors else [],
                'thumbnail_url': b.thumbnail_url,
                'average_rating': b.average_rating,
                'is_manga': b.is_manga,
                'is_novel': b.is_novel
            } for b in books],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }), 200
    
    return render_template('books/list.html', books=books, pagination=pagination)

@bp.route('/books/<int:book_id>/bookmark', methods=['POST', 'DELETE'])
@login_required
def toggle_bookmark(book_id):
    """Add or remove book from user's bookmarks"""
    book = Book.query.get_or_404(book_id)
    
    bookmark = Bookmark.query.filter_by(
        user_id=current_user.id,
        book_id=book_id
    ).first()
    
    if request.method == 'POST':
        if bookmark:
            return jsonify({'message': 'Book already bookmarked'}), 200
        
        notes = request.get_json().get('notes', '') if request.is_json else request.form.get('notes', '')
        
        bookmark = Bookmark(
            user_id=current_user.id,
            book_id=book_id,
            notes=notes
        )
        db.session.add(bookmark)
        db.session.commit()
        
        return jsonify({'message': 'Book bookmarked successfully'}), 201
    
    else:  # DELETE
        if not bookmark:
            return jsonify({'error': 'Bookmark not found'}), 404
        
        db.session.delete(bookmark)
        db.session.commit()
        
        return jsonify({'message': 'Bookmark removed successfully'}), 200

@bp.route('/bookmarks')
@login_required
def my_bookmarks():
    """Get current user's bookmarked books"""
    bookmarks = Bookmark.query.filter_by(user_id=current_user.id).all()
    
    if request.is_json:
        return jsonify({
            'bookmarks': [{
                'id': b.id,
                'book': {
                    'id': b.book.id,
                    'title': b.book.title,
                    'authors': json.loads(b.book.authors) if b.book.authors else [],
                    'thumbnail_url': b.book.thumbnail_url,
                    'average_rating': b.book.average_rating
                },
                'notes': b.notes,
                'created_at': b.created_at.isoformat()
            } for b in bookmarks]
        }), 200
    
    return render_template('books/bookmarks.html', bookmarks=bookmarks)
