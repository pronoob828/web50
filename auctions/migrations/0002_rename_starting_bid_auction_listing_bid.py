# Generated by Django 4.0.5 on 2022-06-06 09:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='auction_listing',
            old_name='starting_bid',
            new_name='bid',
        ),
    ]
