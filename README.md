# Redis Based URL Shortener

A high-performance URL shortening service built with Django REST Framework and Redis. This project demonstrates the power of Redis as a primary data store for applications requiring quick access and expiring data.

## 📋 Overview

This URL shortener converts long URLs into short, easy-to-share links, while tracking click analytics. Redis is used as the main database for its blazing-fast performance, with optional PostgreSQL backup for persistence.

### Key Features

- ⚡ High-performance URL shortening with Redis
- 🔗 Base62 encoding for compact short URLs
- 📊 Click tracking and analytics
- ⏱️ Automatic URL expiration after 30 days
- 🔄 Intelligent caching for frequently accessed URLs
- 🔍 Detailed Redis operation logging

## 🛠️ Technology Stack

- **Django & Django REST Framework**: Web framework and API
- **Redis**: Primary data store and caching
- **PostgreSQL** (optional): Persistent backup storage
- **Python 3.8+**: Core programming language

## 🚀 Installation

### Prerequisites

- Python 3.8+
- Redis Server
- PostgreSQL (optional)

### Setting Up Redis on Ubuntu 22.04

```bash
# Update package lists
sudo apt update

# Install Redis server
sudo apt install redis-server -y

# Configure Redis as a service
sudo sed -i 's/supervised no/supervised systemd/g' /etc/redis/redis.conf

# Restart Redis service
sudo systemctl restart redis

# Verify Redis is running
redis-cli ping  # Should return "PONG"
```

### Project Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/redis-based-url-shortener.git
cd redis-based-url-shortener

# Create and activate virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Run the development server
python manage.py runserver
```

## 📝 Usage

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/shorten/` | POST | Create a short URL |
| `/api/analytics/<short_code>/` | GET | Get analytics for a short URL |
| `/<short_code>/` | GET | Redirect to original URL |

### Creating a Short URL

```bash
curl -X POST http://localhost:8000/api/shorten/ \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.example.com/very/long/url/path"}'
```

Response:
```json
{
  "original_url": "https://www.example.com/very/long/url/path",
  "short_url": "http://localhost:8000/Abc123d",
  "short_code": "Abc123d"
}
```

### Viewing Analytics

```bash
curl http://localhost:8000/api/analytics/Abc123d/
```

Response:
```json
{
  "short_code": "Abc123d",
  "original_url": "https://www.example.com/very/long/url/path",
  "click_count": 5,
  "short_url": "http://localhost:8000/Abc123d"
}
```

## 🏗️ Architecture

The application follows a clean, modular architecture:

1. **Redis Data Structure**:
   - `url:{short_code}`: Maps short codes to original URLs (30-day TTL)
   - `clicks:{short_code}`: Tracks click counts (30-day TTL)
   - `cache:url:{short_code}`: Caches frequent URL lookups (1-hour TTL)
   - `next_url_id`: Counter for generating unique IDs

2. **Core Components**:
   - `services.py`: Redis business logic
   - `views.py`: API endpoints
   - `serializers.py`: Request/response serialization

3. **Workflow**:
   - Generate unique short code using incremental IDs
   - Store URL mapping in Redis with expiration
   - Redirect users while tracking analytics
   - Cache frequently accessed URLs

## 🔧 Configuration

Key settings in `settings.py`:

```python
# Redis connection
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

# URL shortener settings
SHORT_URL_DOMAIN = 'http://localhost:8000'
SHORT_CODE_LENGTH = 7
URL_EXPIRY_DAYS = 30
CACHE_EXPIRY_HOURS = 1
```

## 📈 Redis Benefits Demonstrated

- **Performance**: In-memory operations for sub-millisecond response times
- **TTL Management**: Automatic expiration of old URLs
- **Atomic Operations**: Reliable counters and IDs
- **Caching**: Optimized performance for popular links

## 🔍 Logging

The application logs all Redis operations to the console, showing real-time interaction with the database:

```
Redis Operation: INCR | Key: next_url_id | Result: 15
Redis Operation: Generate Short Code | ID: 15 | Result: 000000f
Redis Operation: SETEX | Key: url:000000f | Result: TTL: 30 days
Redis Operation: SETEX | Key: clicks:000000f | Result: 0 clicks
```

## 🚧 Future Enhancements

- Custom short code support
- User authentication and management
- Advanced analytics (referrer tracking, geolocation)
- Rate limiting for API endpoints
- Redis cluster support for high availability

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

Dhruv Sharma - https://github.com/dhruvsh1997

---

Built with ❤️ and Redis