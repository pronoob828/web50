from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("check_login",views.check_login,name="check_login"),
    path("create_post", views.create_post, name="create_post"),
    path("show_posts/<int:page_no>",views.show_posts,name="show_posts"),
    path("like_post/<int:post_id>",views.like_post, name="like_post"),
    path("show_post/<int:post_id>",views.show_post,name="show_post"),
    path("post_comment/<int:post_id>",views.post_comment,name="post_comment"),
    path("like_comment/<int:comment_id>",views.like_comment,name="like_comment"),
    path("get_post_like_count/<int:post_id>",views.get_post_like_count,name="get_post_like_count"),
    path("get_comment_like_count/<int:comment_id>",views.get_comment_like_count,name="get_comment_like_count"),
    path("get_pages_count",views.get_pages_count,name="get_pages_count"),
    path("edit_post/<int:post_id>",views.edit_post,name="edit_post"),
    path("get_user_details/<int:user_id>",views.get_user_details,name="get_user_details"),
    path("show_user_posts/<int:user_id>",views.show_user_posts,name="show_user_posts"),
    path("check_follow_conditions/<int:user_id>",views.check_follow_conditions, name="check_follow_conditions"),
    path("follow_user/<int:user_id>",views.follow_user,name="follow_user"),
    path("unfollow_user/<int:user_id>",views.unfollow_user,name="unfollow_user"),
    path("get_follower_count/<int:user_id>",views.get_follower_count,name="get_follower_count"),
    path("following_page",views.following_page,name="following_page"),
    path("get_user_followers/<int:user_id>",views.get_user_followers,name="get_user_followers")
]
