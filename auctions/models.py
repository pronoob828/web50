from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime



class User(AbstractUser):
    pass

Categories = (
    ('Automotive','Automotive'),
    ('Smart Devices','Smart Devices'),
    ('Electronics','Electronics'),
    ('Fashion','Fashion'),
    ('Beauty','Beauty'),
    ('Toys','Toys'),
    ('Sports','Sports'),
    ('Books','Books'),
    ('Art','Art'),
    ('Furniture','Furniture'),
    ('Other', 'Other')
) 

class auction_listing(models.Model):

    title = models.CharField(max_length=80)
    description = models.TextField(max_length=600)
    owner = models.ForeignKey(User,on_delete=models.CASCADE,related_name="user_listings")
    starting_bid = models.IntegerField()
    image = models.URLField(blank=True)
    category = models.CharField(choices=Categories,max_length=100,default='Other')
    listing_time = models.DateTimeField(auto_now_add=True)
    open = models.BooleanField(default=True)

    def __str__(self):
        formatted_time = self.listing_time.strftime("%d/%m/%Y, %H:%M:%S")
        return f"By -- {self.owner.username} -- {self.title} -- {formatted_time}"


class bid(models.Model):
    amount = models.IntegerField()
    bidder = models.ForeignKey(User,on_delete=models.CASCADE,related_name="bids")
    listing = models.ForeignKey(auction_listing,on_delete=models.CASCADE,related_name="listings_bid_on")
    bid_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        formatted_time = self.bid_time.strftime("%d/%m/%Y, %H:%M:%S")
        return f"By -- {self.bidder.username} -- ${self.amount} -- On -- {self.listing.title} -- {formatted_time}"

class comment(models.Model):
    comment_text = models.TextField(max_length=500)
    commenter = models.ForeignKey(User,on_delete=models.CASCADE,related_name="comments")
    listing = models.ForeignKey(auction_listing,on_delete=models.CASCADE,related_name="commented_listings")
    comment_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        formatted_time = self.comment_time.strftime("%d/%m/%Y, %H:%M:%S")
        return f"{self.commenter.username} -- commented -- {self.comment_text[:70]}... -- on -- {self.listing.title} -- {formatted_time}"

class watchlist(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="watchlist_user")
    listing = models.ForeignKey(auction_listing,on_delete=models.CASCADE,related_name="watchlist_listing")

    def __str__(self):
        return f"{self.user.username} -- added -- {self.listing.title} -- to watchlist"