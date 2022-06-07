from datetime import datetime
from django import http
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

import datetime
from django import forms
from django.db.models import Max
from django.contrib.auth.decorators import login_required

from .models import User, auction_listing, comment, bid, watchlist, Categories


# I dont't feel like installing pytz for this so just a botch job for now to not throw me off
def get_saudi_time():

    now = datetime.datetime.now()
    my_timezone_adjustment = datetime.timedelta(hours=3)
    now = now - my_timezone_adjustment
    now = now.replace(tzinfo=datetime.timezone.utc)
    return now


def index(request):
    return render(
        request,
        "auctions/index.html",
        {
            "listings": auction_listing.objects.filter(open=True).order_by('-listing_time'),
            "current_time": get_saudi_time(),
        },
    )


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
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "auctions/login.html")


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
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def display_listing(request, listing_id):

    listing = auction_listing.objects.get(pk=listing_id)
    bids = bid.objects.filter(listing=listing)
    try:
        max_bid_amount = bid.objects.filter(listing=listing).aggregate(Max("amount"))[
            "amount__max"
        ]
        winner_bid = bid.objects.get(amount=max_bid_amount)
        winner = User.objects.get(bids=winner_bid)
    except:
        max_bid_amount = listing.starting_bid
        winner_bid = listing.starting_bid
        winner = None

    comments = comment.objects.filter(listing=listing).order_by('-comment_time')

    if request.user.is_authenticated:
        if watchlist.objects.filter(user=request.user, listing=listing).count() == 1:
            in_watchlist = True
        elif watchlist.objects.filter(user=request.user, listing=listing).count() == 0:
            in_watchlist = False
        else:
            return HttpResponse(
                "<br><br><br><center><h1>Something went really wrong 118</h1></center>"
            )
    else:
        in_watchlist=False

    return render(
        request,
        "auctions/listing.html",
        {
            "listing": listing,
            "current_time": get_saudi_time(),
            "comments": comments,
            "current_bid": max_bid_amount,
            "bids": bids,
            "winner": winner,
            "in_watchlist": in_watchlist
        },
    )


@login_required
def add_comment(request):

    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        listing = auction_listing.objects.get(id=listing_id)
        commenter = request.user
        comment_text = request.POST["comment"]
        if comment_text:
            try:
                new_comment = comment(
                    comment_text=comment_text, commenter=commenter, listing=listing
                )
                new_comment.save()
            except:
                return HttpResponse(
                    "<br><br><br><center><h1>Something went wrong 141</h1></center>"
                )

    return HttpResponseRedirect(reverse("display", args=[listing_id]))


@login_required
def palce_bid(request):

    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        try:
            bid_amount = int(request.POST["amount"])
        except:
            return HttpResponse(
                "<br><br><br><center><h1>Bid amount must be integer</h1></center>"
            )
        bidder = request.user
        listing = auction_listing.objects.get(id=listing_id)

        bids = bid.objects.filter(listing=auction_listing.objects.get(pk=listing_id))
        current_max = bids.aggregate(Max("amount"))["amount__max"]
        if current_max == None:
            current_max = listing.starting_bid
        print(bidder)
        print(listing.owner)
        if bidder != listing.owner:
            if bid_amount > current_max:
                try:
                    new_bid = bid(amount=bid_amount, bidder=bidder, listing=listing)
                    new_bid.save()
                except:
                    return HttpResponse(
                        "<br><br><br><center><h1>Something Went Wrong 169</h1></center>"
                    )
            else:
                return HttpResponse(
                    "<br><br><br><center><h1>Bid must be higher than current bid</h1></center>"
                )
        else:
            return HttpResponse(
                "<br><br><br><center><h1>You can't bid on your own listing</h1></center>"
            )

    return HttpResponseRedirect(reverse("display", args=[listing_id]))

def winner_of(listing_id):
    listing = auction_listing.objects.get(pk=listing_id)
    try:
        max_bid_amount = bid.objects.filter(listing=listing).aggregate(Max("amount"))[
            "amount__max"
        ]
        winner_bid = bid.objects.get(amount=max_bid_amount)
        winner = User.objects.get(bids=winner_bid)
    except:
        max_bid_amount = listing.starting_bid
        winner_bid = listing.starting_bid
        winner = "None"

    return winner


@login_required
def close_listing(request):

    if request.method == "POST":
        # try:
        listing_id = int(request.POST["listing_id"])
        # except:
        #   return HttpResponse("<br><br><br><center><h1>How did you get here?!</h1></center>")
        closer = request.user
        listing = auction_listing.objects.get(id=listing_id)

        if closer == listing.owner:
            listing.open = False
            listing.save()
            if watchlist.objects.filter(listing = listing).count() == 0:
                new_watchlist = watchlist(user = winner_of(listing_id),listing = listing)
                new_watchlist.save()
        else:
            return HttpResponse(
                "<br><br><br><center><h1>What do you think you're doing</h1></center>"
            )

    return HttpResponseRedirect(reverse("display", args=[listing_id]))


@login_required
def show_watchlist(request):

    watchlists = watchlist.objects.filter(user=request.user)

    return render(
        request,
        "auctions/watchlist.html",
        {"watchlists": watchlists, "current_time": get_saudi_time()},
    )


@login_required
def add_to_watchlist(request):

    if request.method == "POST":
        listing_id = int(request.POST["listing_id"])
        listing = auction_listing.objects.get(pk=listing_id)
        try:
            if (
                watchlist.objects.filter(user=request.user, listing=listing).count()
                == 0
            ):
                New_watchlist = watchlist(user=request.user, listing=listing)
                New_watchlist.save()
            else:
                return HttpResponse(
                    "<br><br><br><center><h1>That shouldn't happen</h1></center>"
                )
        except:
            return HttpResponse(
                "<br><br><br><center><h1>Something went wrong 213</h1></center>"
            )

        return HttpResponseRedirect(reverse("display", args=[listing_id]))


@login_required
def remove_from_watchlist(request):

    if request.method == "POST":
        listing_id = int(request.POST["listing_id"])
        listing = auction_listing.objects.get(pk=listing_id)
        try:
            watchlist.objects.filter(listing=listing).delete()
        except:
            return HttpResponse(
                "<br><br><br><center><h1>Something went wrong 226</h1></center>"
            )

        return HttpResponseRedirect(reverse("display", args=[listing_id]))

@login_required
def create_listing(request):
    if request.method=="POST":

        title = request.POST["title"]
        description = request.POST["description"]
        owner = request.user
        starting_bid = int(request.POST["starting_bid"])
        image = request.POST["image_url"]
        category = request.POST["category"]

        new_listing = auction_listing(title=title,description=description,owner=owner,starting_bid=starting_bid,image=image,category=category)
        new_listing.save()
        return HttpResponseRedirect(reverse("display", args=[new_listing.id]))

    
    available_choices = []
    for option in Categories:
        available_choices.append(option[1])
    print(available_choices)

    return render(request,"auctions/create.html",{"categories":available_choices})

def all_categories(request):
    available_choices = []
    for option in Categories:
        available_choices.append(option[1])
    print(available_choices)
    return render(request,"auctions/categories.html",{"categories":available_choices})

def show_category(request,category):
    listings = auction_listing.objects.filter(open=True, category=category).order_by('-listing_time')
    return render(request,"auctions/category.html",{
        "listings":listings,
        "category":category,
        "current_time":get_saudi_time()
    })

def my_listings(request):
    listings = auction_listing.objects.filter(owner = request.user).order_by("-listing_time")
    return render(request,"auctions/my_listings.html",{
        "listings":listings,
        "current_time":get_saudi_time()
    })

def quick_remove_from_watchlist(request):

    if request.method == "POST":
        listing_id = int(request.POST["listing_id"])
        listing = auction_listing.objects.get(pk=listing_id)
        try:
            watchlist.objects.filter(listing=listing).delete()
        except:
            return HttpResponse(
                "<br><br><br><center><h1>Something went wrong 226</h1></center>"
            )

        return HttpResponseRedirect(reverse("show_watchlist"))