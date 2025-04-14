# shortener/views.py

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import redirect
from django.conf import settings
from .serializers import URLShortenerSerializer, URLResponseSerializer, AnalyticsSerializer
from .services import (
    create_short_url, get_original_url, track_click,
    get_click_count, url_exists, backup_to_db
)

class ShortenURLView(APIView):
    """API endpoint to create short URLs"""
    
    def post(self, request):
        serializer = URLShortenerSerializer(data=request.data)
        if serializer.is_valid():
            original_url = serializer.validated_data['url']
            custom_code = serializer.validated_data.get('custom_code', '')
            
            # TODO: Handle custom code logic
            short_code = create_short_url(original_url)
            
            # Construct the short URL
            short_url = f"{settings.SHORT_URL_DOMAIN}/{short_code}"
            
            # Optional: Backup to DB
            # backup_to_db(short_code, original_url, 0)
            
            response_data = {
                'original_url': original_url,
                'short_url': short_url,
                'short_code': short_code
            }
            
            response_serializer = URLResponseSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class URLAnalyticsView(APIView):
    """API endpoint to get URL analytics"""
    
    def get(self, request, short_code):
        if not url_exists(short_code):
            return Response(
                {"error": "URL not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        original_url = get_original_url(short_code)
        click_count = get_click_count(short_code)
        short_url = f"{settings.SHORT_URL_DOMAIN}/{short_code}"
        
        data = {
            'short_code': short_code,
            'original_url': original_url,
            'click_count': click_count,
            'short_url': short_url
        }
        
        serializer = AnalyticsSerializer(data)
        return Response(serializer.data)

# This view will be in a separate file for URL redirection
def redirect_to_original(request, short_code):
    """Redirect short URLs to original URLs"""
    original_url = get_original_url(short_code)
    
    if original_url:
        # Track click
        track_click(short_code)
        return redirect(original_url)
    
    # URL not found
    return Response(
        {"error": "URL not found"},
        status=status.HTTP_404_NOT_FOUND
    )