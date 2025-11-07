import requests
import os
import json

class GoogleBooksAPI:
    """Client for Google Books API"""
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_BOOKS_API_KEY', '')
    
    def search(self, query, max_results=10, start_index=0):
        """Search for books using Google Books API"""
        params = {
            'q': query,
            'maxResults': min(max_results, 40),
            'startIndex': start_index
        }
        if self.api_key:
            params['key'] = self.api_key
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching from Google Books API: {e}")
            return {'items': []}
    
    def get_book(self, volume_id):
        """Get detailed information about a specific book"""
        params = {}
        if self.api_key:
            params['key'] = self.api_key
        
        try:
            response = requests.get(f"{self.BASE_URL}/{volume_id}", params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching book from Google Books API: {e}")
            return None
    
    @staticmethod
    def parse_book_data(item):
        """Parse Google Books API response item into standardized format"""
        volume_info = item.get('volumeInfo', {})
        
        return {
            'google_books_id': item.get('id'),
            'title': volume_info.get('title', 'Unknown Title'),
            'authors': json.dumps(volume_info.get('authors', [])),
            'description': volume_info.get('description', ''),
            'categories': json.dumps(volume_info.get('categories', [])),
            'publisher': volume_info.get('publisher', ''),
            'published_date': volume_info.get('publishedDate', ''),
            'page_count': volume_info.get('pageCount'),
            'language': volume_info.get('language', ''),
            'isbn': volume_info.get('industryIdentifiers', [{}])[0].get('identifier', ''),
            'thumbnail_url': volume_info.get('imageLinks', {}).get('thumbnail', ''),
            'preview_link': volume_info.get('previewLink', ''),
            'info_link': volume_info.get('infoLink', ''),
            'average_rating': volume_info.get('averageRating', 0.0),
            'ratings_count': volume_info.get('ratingsCount', 0)
        }


class OpenLibraryAPI:
    """Client for Open Library API"""
    BASE_URL = "https://openlibrary.org"
    
    def search(self, query, limit=10, offset=0):
        """Search for books using Open Library API"""
        params = {
            'q': query,
            'limit': limit,
            'offset': offset
        }
        
        try:
            response = requests.get(f"{self.BASE_URL}/search.json", params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching from Open Library API: {e}")
            return {'docs': []}
    
    def get_book(self, book_id):
        """Get detailed information about a specific book"""
        try:
            response = requests.get(f"{self.BASE_URL}/works/{book_id}.json", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching book from Open Library API: {e}")
            return None
    
    @staticmethod
    def parse_book_data(doc):
        """Parse Open Library API response doc into standardized format"""
        return {
            'open_library_id': doc.get('key', '').replace('/works/', ''),
            'title': doc.get('title', 'Unknown Title'),
            'authors': json.dumps(doc.get('author_name', [])),
            'description': doc.get('first_sentence', [''])[0] if doc.get('first_sentence') else '',
            'categories': json.dumps(doc.get('subject', [])[:10]),  # Limit to top 10 subjects
            'publisher': ', '.join(doc.get('publisher', [])[:3]) if doc.get('publisher') else '',
            'published_date': str(doc.get('first_publish_year', '')),
            'language': doc.get('language', [''])[0] if doc.get('language') else '',
            'isbn': doc.get('isbn', [''])[0] if doc.get('isbn') else '',
            'thumbnail_url': f"https://covers.openlibrary.org/b/id/{doc['cover_i']}-M.jpg" if doc.get('cover_i') else ''
        }
