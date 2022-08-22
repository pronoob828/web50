from django.urls import path

from . import views,util

app_name = "encyclopedia"
urlpatterns = [
    path("", views.index, name="index"),
    path("<str:entry>",views.display,name="display_entry"),
    path("search/",views.search,name="search"),
    path("create/",views.create,name="create"),
    path("edit/",views.edit,name="edit"),
    path("random/",views.rand,name="random")
]
