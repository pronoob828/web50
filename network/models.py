from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "date_joined": self.date_joined.strftime("%b %d %Y"),
        }


class Post(models.Model):
    poster = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_posts"
    )
    post_body = models.TextField(max_length=600)
    post_likes = models.ManyToManyField(User, related_name="posts_liked")
    post_comments = models.ManyToManyField(
        User, through="Comments", related_name="comments"
    )
    post_add_time = models.DateTimeField(auto_now_add=True)
    post_update_time = models.DateTimeField(auto_now=True)

    def serialize(self):
        return {
            "id": self.id,
            "poster": self.poster.serialize(),
            "post_body": self.post_body,
            "post_add_time": self.post_add_time.strftime("%b %d %Y, %I:%M %p"),
            "post_update_time": self.post_update_time.strftime("%b %d %Y, %I:%M %p"),
            "post_like_count": self.post_likes.all().count(),
            "post_comment_count": self.post_comments.all().count(),
            "post_likes": [user.serialize() for user in self.post_likes.all()],
            "post_comments": [
                user.serialize()
                for user in self.comments_on_post.all().order_by("-comment_add_time")
            ],
        }
    def __str__(self):
        return f"{self.id} \{self.poster.username} posted {self.post_body[:50]}"


class Comments(models.Model):
    commenter = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="User_comments"
    )
    post_commented_on = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments_on_post"
    )
    comment_body = models.TextField(max_length=300)
    comment_add_time = models.DateTimeField(auto_now_add=True)
    comment_likes = models.ManyToManyField(User, related_name="comments_liked")

    def serialize(self):
        return {
            "comment_id": self.id,
            "commenter": self.commenter.serialize(),
            "comment_body": self.comment_body,
            "comment_add_time": self.comment_add_time.strftime("%b %d %Y, %I:%M %p"),
            "comment_likes": [user.serialize() for user in self.comment_likes.all()],
            "comment_like_count": self.comment_likes.all().count(),
        }


class Follows(models.Model):
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_following"
    )
    followed = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_followers"
    )

    def serialize(self):
        return {
            "follower": self.follower.serialize(),
            "followed": self.followed.serialize(),
        }

    def __str__(self):
        return f"{self.follower} followed {self.followed}"
