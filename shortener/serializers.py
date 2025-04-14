# shortener/serializers.py

from rest_framework import serializers
from django.conf import settings

class URLShortenerSerializer(serializers.Serializer):
    url = serializers.URLField(max_length=2048)
    custom_code = serializers.CharField(max_length=10, required=False, allow_blank=True)
    
    def validate_url(self, value):
        """Validate URL"""
        if len(value) < 10:
            raise serializers.ValidationError("URL is too short")
        return value
    
    def validate_custom_code(self, value):
        """Validate custom code if provided"""
        if value:
            if len(value) > 10:
                raise serializers.ValidationError("Custom code cannot be longer than 10 characters")
            # Further validation can be added here
        return value

class URLResponseSerializer(serializers.Serializer):
    original_url = serializers.URLField()
    short_url = serializers.URLField()
    short_code = serializers.CharField()

class AnalyticsSerializer(serializers.Serializer):
    short_code = serializers.CharField()
    original_url = serializers.URLField()
    click_count = serializers.IntegerField()
    short_url = serializers.URLField()