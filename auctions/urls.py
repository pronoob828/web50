from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("<int:listing_id>",views.display_listing,name="display"),
    path("add_comment",views.add_comment,name="add_comment"),
    path("place_bid",views.palce_bid,name="place_bid"),
    path("close_listing",views.close_listing,name="close_listing"),
    path("watchlist",views.show_watchlist,name="show_watchlist"),
    path("add_to_watchlist",views.add_to_watchlist,name="add_to_watchlist"),
    path("remove_from_watchlist",views.remove_from_watchlist,name="remove_from_watchlist"),
    path("create_listing",views.create_listing,name="create_listing"),
    path("categories",views.all_categories,name="all_categories"),
    path("categories/<str:category>",views.show_category,name="show_category"),
    path("my_listings",views.my_listings,name="my_listings"),
    path("quick_remove_from_watchlist",views.quick_remove_from_watchlist,name="quick_remove_from_watchlist")
]
