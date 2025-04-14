# shortener/urls.py

from django.urls import path
from .views import ShortenURLView, URLAnalyticsView

urlpatterns = [
    path('shorten/', ShortenURLView.as_view(), name='shorten_url'),
    path('analytics/<str:short_code>/', URLAnalyticsView.as_view(), name='url_analytics'),
]