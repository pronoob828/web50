from unicodedata import category
from django.contrib import admin

from  .models import User, auction_listing, bid, comment, watchlist
from django.utils.html import format_html
# Register your models here.

class listingAdmin(admin.ModelAdmin):

    list_display = ('owner', 'image_preview','title','listing_time','category','open')
    list_display_links = ('owner', 'image_preview','title')
    list_filter = ('open','listing_time','category')

    def image_preview(self,obj):
        return format_html(f"<img src = {obj.image} width='50px'>")


admin.site.register(User)
admin.site.register(auction_listing,listingAdmin)
admin.site.register(bid)
admin.site.register(comment)
admin.site.register(watchlist)