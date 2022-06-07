from django import template
from django.db.models import Max

from auctions.models import bid, auction_listing

register = template.Library()

@register.filter(name='winner_of')
def winner_of(listing_id):
    
    listing = auction_listing.objects.get(pk=listing_id)
    try:
        max_bid_amount = bid.objects.filter(listing=listing).aggregate(Max("amount"))[
            "amount__max"
        ]
    except:
        max_bid_amount = listing.starting_bid    
    return max_bid_amount
