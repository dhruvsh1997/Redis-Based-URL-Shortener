# shortener/models.py

from django.db import models

class URLMapping(models.Model):
    short_code = models.CharField(max_length=10, primary_key=True)
    original_url = models.URLField(max_length=2048)
    created_at = models.DateTimeField(auto_now_add=True)
    click_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.short_code} -> {self.original_url}"