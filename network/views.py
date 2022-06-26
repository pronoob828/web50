from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from yaml import serialize

from .models import User, Post, Comments, Follows
import json
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils.html import strip_tags


def index(request):
    return render(request, "network/index.html")


def following_page(request):
    users_following = request.user.user_following.all()
    following_list = []
    for object in users_following:
        following_list.append(object.followed)
    posts = Post.objects.filter(poster__in = following_list).order_by("-post_add_time").all()
    serialized_data = [post.serialize() for post in posts]
    for post in serialized_data:
        if request.user.is_authenticated:
            if is_liked(request, post["id"]):
                post["liked"] = True
            else:
                post["liked"] = False
        else:
            post["liked"] = None

    return JsonResponse(serialized_data, safe=False)


def get_pages_count(request):
    pages = Paginator(Post.objects.all().order_by("-post_add_time").all(), 10)
    page_count = pages.num_pages
    return JsonResponse({"pages_count": page_count})


def show_posts(request, page_no):
    posts_to_show = Paginator(Post.objects.all().order_by("-post_add_time").all(), 10)
    page = posts_to_show.page(page_no).object_list

    serialized_data = [post.serialize() for post in page]
    for post in serialized_data:
        if request.user.is_authenticated:
            if is_liked(request, post["id"]):
                post["liked"] = True
            else:
                post["liked"] = False
            if request.user.id == post["poster"]["id"]:
                post["users_own_post"] = True
            else:
                post["users_own_post"] = False
        else:
            post["liked"] = None
            post["users_own_post"] = None

    return JsonResponse(serialized_data, safe=False)


def comment_is_liked(request, comment_id):
    comment_to_test = Comments.objects.get(id=comment_id)
    if request.user in comment_to_test.comment_likes.all():
        return True
    else:
        return False


def is_liked(request, post_id):
    post_to_test = Post.objects.get(id=post_id)
    if request.user in post_to_test.post_likes.all():
        return True
    else:
        return False


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "network/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "network/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request, "network/register.html", {"message": "Username already taken."}
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required
def create_post(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=400)

    data = json.loads(request.body)
    data = strip_tags(data)
    if data["post_text"]:
        new_post = Post(poster=request.user, post_body=data["post_text"])
        new_post.save()
        return JsonResponse({"message": "success."}, status=201)
    else:
        return JsonResponse({"message": "Text area cannot be empty"}, status=404)


@login_required
def like_post(request, post_id):

    if request.method == "PUT":
        data = json.loads(request.body)
        post = Post.objects.get(id=post_id)
        action = data["action"]
        if action == "like":
            post.post_likes.add(request.user)
        elif action == "unlike":
            post.post_likes.remove(request.user)
        return HttpResponse(status=204)


@login_required
def like_comment(request, comment_id):
    if request.method == "PUT":
        data = json.loads(request.body)
        comment = Comments.objects.get(id=comment_id)
        action = data["action"]
        if action == "like":
            comment.comment_likes.add(request.user)
        elif action == "unlike":
            comment.comment_likes.remove(request.user)
    return HttpResponse(status=204)


def show_post(request, post_id):

    try:
        post = Post.objects.get(id=post_id)
    except:
        return JsonResponse({"message": "Post not found"}, status=404)
    serialized_post = post.serialize()
    if request.user.is_authenticated:
        if request.user in post.post_likes.all():
            serialized_post["liked"] = True
        else:
            serialized_post["liked"] = False
        if request.user.id == post.poster.id:
            serialized_post["users_own_post"] = True
        else:
            serialized_post["users_own_post"] = False
    else:
        serialized_post["liked"] = None
        serialized_post["users_own_post"] = False

    for comment in serialized_post["post_comments"]:
        if request.user.is_authenticated:
            if comment_is_liked(request, comment["comment_id"]):
                comment["comment_is_liked"] = True
            else:
                comment["comment_is_liked"] = False
        else:
            comment["comment_is_liked"] = False

    return JsonResponse(serialized_post, safe=False)


@login_required
def post_comment(request, post_id):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=400)

    post = Post.objects.get(id=post_id)
    data = json.loads(request.body)
    comment_text = data["comment_text"]
    if comment_text:
        new_comment = Comments(
            commenter=request.user, post_commented_on=post, comment_body=comment_text
        )
        new_comment.save()
        return JsonResponse({"message": "success."}, status=201)
    else:
        return JsonResponse({"message": "Comment cannot be empty"}, status=404)


def check_login(request):
    if request.user.is_authenticated:
        return JsonResponse({"is_authenticated": True})
    else:
        return JsonResponse({"is_authenticated": False})


def get_post_like_count(request, post_id):
    like_count = Post.objects.get(id=post_id).post_likes.count()
    return JsonResponse({"like_count": like_count})


def get_comment_like_count(request, comment_id):
    like_count = Comments.objects.get(id=comment_id).comment_likes.count()
    return JsonResponse({"like_count": like_count})


def get_user_details(request, user_id):
    selected_user = User.objects.get(id=user_id)
    user = selected_user.serialize()
    serialized_data = user
    serialized_data["follower_count"] = selected_user.user_followers.count()
    serialized_data["following_count"] = selected_user.user_following.count()

    if request.user.is_authenticated:
        if is_followed(request, selected_user):
            serialized_data["is_followed"] = True
        else:
            serialized_data["is_followed"] = False
    else:
        serialized_data["is_followed"] = None

    return JsonResponse({"user": user})


def show_user_posts(request, user_id):
    selected_user = User.objects.get(id=user_id)
    user_posts = selected_user.user_posts.all().order_by("-post_add_time")
    serialized_data = [post.serialize() for post in user_posts]
    for post in serialized_data:
        if request.user.is_authenticated:
            if is_liked(request, post["id"]):
                post["liked"] = True
            else:
                post["liked"] = False
            if request.user.id == post["poster"]["id"]:
                post["users_own_post"] = True
            else:
                post["users_own_post"] = False
        else:
            post["liked"] = None
            post["users_own_post"] = None
    return JsonResponse(serialized_data, safe=False)


def is_followed(request, followed_user):
    test_obj = Follows(follower=request.user, followed=followed_user)
    for object in request.user.user_following.all():
        if (
            test_obj.follower == object.follower
            and test_obj.followed == object.followed
        ):
            return True
    return False


@login_required
def edit_post(request, post_id):

    if request.method == "PUT":
        data = json.loads(request.body)
        content = data["content"]
        # content = content.replace("\n", " ")
        try:
            post_to_edit = Post.objects.get(poster=request.user, id=post_id)
            post_to_edit.post_body = content
            post_to_edit.save()
        except:
            return JsonResponse({"error": "Something went wrong."}, status=403)
    return JsonResponse({"new_content": content})


def check_follow_conditions(request, user_id):
    user = User.objects.get(id=user_id)
    data = {}
    if request.user.is_authenticated:
        if request.user != user:
            data["is_self"] = False
            if is_followed(request, user):
                data["is_followed"] = True
            else:
                data["is_followed"] = False
        else:
            data["is_followed"] = None
            data["is_self"] = True

    else:
        data["is_self"] = None
        data["is_followed"] = None
    return JsonResponse(
            {"is_self": data["is_self"], "is_followed": data["is_followed"]}
        )


@login_required
def follow_user(request, user_id):
    if request.user.is_authenticated:
        if request.method == "PUT":
            try:
                user_to_be_followed = User.objects.get(id=user_id)
                if not is_followed(request, user_to_be_followed):
                    new_follow = Follows(
                        follower=request.user, followed=user_to_be_followed
                    )
                    new_follow.save()
            except:
                return JsonResponse({"error": "Something went wrong."}, status=403)
            return JsonResponse({"message": "success"}, status=200)


@login_required
def unfollow_user(request, user_id):
    if request.user.is_authenticated:
        if request.method == "PUT":
            try:
                user_to_be_unfollowed = User.objects.get(id=user_id)
                Follows.objects.get(
                    follower=request.user, followed=user_to_be_unfollowed
                ).delete()
            except:
                return JsonResponse({"error": "Something went wrong."}, status=403)
            return JsonResponse({"message": "success"}, status=200)


def get_follower_count(request, user_id):
    count = User.objects.get(id=user_id).user_followers.count()
    return JsonResponse({"follower_count": count})


def get_user_followers(request, user_id):
    user = User.objects.get(id = user_id)
    followers = []
    if request.user == user:
        follower_objects = user.user_followers.all()
        for object in follower_objects:
            followers.append(object.follower.serialize())
    followers.reverse()
    return JsonResponse({"followers":followers})