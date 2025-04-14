# shortener/services.py

import redis
import string
import random
import logging
from django.conf import settings
import time

# Configure logging
logger = logging.getLogger(__name__)

# Redis connection
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True
)

def log_redis_operation(operation, key, result=None):
    """Log Redis operations for demonstration"""
    logger.info(f"Redis Operation: {operation} | Key: {key} | Result: {result}")
    # Print to console for demonstration
    print(f"Redis Operation: {operation} | Key: {key} | Result: {result}")

def generate_short_code(length=settings.SHORT_CODE_LENGTH):
    """Generate a random short code using Base62 encoding (a-zA-Z0-9)"""
    characters = string.ascii_letters + string.digits
    
    # Use Redis to generate a unique ID
    next_id = redis_client.incr("next_url_id")
    log_redis_operation("INCR", "next_url_id", next_id)
    
    # Convert to Base62
    result = ""
    base = len(characters)
    
    # Convert the number to Base62
    id_value = next_id
    while id_value > 0:
        result = characters[id_value % base] + result
        id_value //= base
        
    # Ensure we have at least 'length' characters
    result = result.zfill(length)
    if len(result) > length:
        result = result[-length:]
        
    log_redis_operation("Generate Short Code", f"ID: {next_id}", result)
    return result

def create_short_url(original_url):
    """Create a short URL from the original URL and store in Redis"""
    # Check if URL already exists in cache
    cache_key = f"cache:reverse:{original_url}"
    short_code = redis_client.get(cache_key)
    log_redis_operation("GET", cache_key, short_code)
    
    if short_code:
        log_redis_operation("Cache Hit", cache_key, "URL already shortened")
        return short_code
    
    # Generate a unique short code
    short_code = generate_short_code()
    
    # Store in Redis with expiry
    url_key = f"url:{short_code}"
    redis_client.setex(url_key, settings.URL_EXPIRY_DAYS * 24 * 60 * 60, original_url)
    log_redis_operation("SETEX", url_key, f"TTL: {settings.URL_EXPIRY_DAYS} days")
    
    # Initialize click counter
    clicks_key = f"clicks:{short_code}"
    redis_client.setex(clicks_key, settings.URL_EXPIRY_DAYS * 24 * 60 * 60, 0)
    log_redis_operation("SETEX", clicks_key, "0 clicks")
    
    # Store reverse mapping in cache
    redis_client.setex(cache_key, settings.CACHE_EXPIRY_HOURS * 60 * 60, short_code)
    log_redis_operation("SETEX", cache_key, f"TTL: {settings.CACHE_EXPIRY_HOURS} hours")
    
    return short_code

def get_original_url(short_code):
    """Retrieve the original URL from Redis"""
    # First check cache
    cache_key = f"cache:url:{short_code}"
    original_url = redis_client.get(cache_key)
    log_redis_operation("GET", cache_key, "Cache hit" if original_url else "Cache miss")
    
    if not original_url:
        # Get from main storage
        url_key = f"url:{short_code}"
        original_url = redis_client.get(url_key)
        log_redis_operation("GET", url_key, "URL found" if original_url else "URL not found")
        
        if original_url:
            # Update cache
            redis_client.setex(cache_key, settings.CACHE_EXPIRY_HOURS * 60 * 60, original_url)
            log_redis_operation("SETEX", cache_key, f"TTL: {settings.CACHE_EXPIRY_HOURS} hours")
    
    return original_url

def track_click(short_code):
    """Increment click counter for a short URL"""
    clicks_key = f"clicks:{short_code}"
    
    # Use pipeline for atomic operations
    with redis_client.pipeline() as pipe:
        # Increment counter
        pipe.incr(clicks_key)
        # Reset expiry time
        pipe.expire(clicks_key, settings.URL_EXPIRY_DAYS * 24 * 60 * 60)
        # Execute commands
        result = pipe.execute()
    
    log_redis_operation("INCR & EXPIRE", clicks_key, f"New count: {result[0]}")
    return result[0]  # Return new count

def get_click_count(short_code):
    """Get the click count for a short URL"""
    clicks_key = f"clicks:{short_code}"
    count = redis_client.get(clicks_key)
    log_redis_operation("GET", clicks_key, count)
    
    return int(count) if count else 0

def url_exists(short_code):
    """Check if a short URL exists in Redis"""
    url_key = f"url:{short_code}"
    exists = redis_client.exists(url_key)
    log_redis_operation("EXISTS", url_key, exists)
    
    return bool(exists)

def backup_to_db(short_code, original_url, click_count):
    """Optional: Backup URL data to PostgreSQL"""
    # Import here to avoid circular imports
    from .models import URLMapping
    
    # Create or update URLMapping
    mapping, created = URLMapping.objects.update_or_create(
        short_code=short_code,
        defaults={
            'original_url': original_url,
            'click_count': click_count
        }
    )
    
    log_redis_operation("DB Backup", f"short_code={short_code}", "Created" if created else "Updated")
    return mapping