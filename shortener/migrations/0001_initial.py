# Generated by Django 5.2 on 2025-04-13 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='URLMapping',
            fields=[
                ('short_code', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('original_url', models.URLField(max_length=2048)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('click_count', models.PositiveIntegerField(default=0)),
            ],
        ),
    ]
