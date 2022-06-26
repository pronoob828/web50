from django.contrib import admin

from .models import User, Post, Comments, Follows
# Register your models here.

admin.site.register(User)
admin.site.register(Post)
admin.site.register(Comments)
admin.site.register(Follows)