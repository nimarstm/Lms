# Generated by Django 5.1.1 on 2024-09-16 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_book_is_borrowed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='publication_date',
            field=models.DateField(blank=True, null=True, verbose_name='Publication Date'),
        ),
    ]
