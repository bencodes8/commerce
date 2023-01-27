from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import User, Listing, Genre, Bid
from .forms import NewListingForm, BidForm

# index page
def index(request):
    listings = Listing.objects.all()

    return render(request, "auctions/index.html", {
        "listings": listings
    })

# create listing page
@login_required
def create(request):
    if request.method == "POST":
        form = NewListingForm(request.POST)
        
        if form.is_valid():
            messages.success(request, 'Successfully added listing.')
            
            genres = request.POST.getlist('genres')
            
            instance = form.save(commit=False)
            instance.owner = request.user
            instance.save()
        
            latest_listing = Listing.objects.latest('listing_id')
            
            for genres_id in genres:
                latest_listing.genres.add(genres_id)

            return HttpResponseRedirect(reverse('index'))
        
        else:
            return render(request, "auctions/create.html", {
                "form": NewListingForm(request.POST)
            })
    return render(request, "auctions/create.html", {
        "form": NewListingForm()
    })

# listing item information
def listing(request, listing_id):
    try:
        listing = Listing.objects.get(pk=listing_id)
    except:
        return HttpResponseNotFound('Sorry, directing you to this listing item lead to an error. Perhaps it was deleted?')
    
    # bid logic
    if request.method == "POST":
        
        if 'bid_amount' in request.POST:
            bid_form = BidForm(request.POST)
            if bid_form.is_valid():
                # keep track of user's bid
                bid_price = float(request.POST['bid'])
                # check to see if the user has already submitted a bid for this listing
                if not Bid.objects.filter(bidder=request.user.id).exists() and bid_price >= listing.starting_bid:
                    instance = bid_form.save(commit=False)
                    instance.bidder = request.user
                    instance.listing = listing
                    instance.bid = bid_price
                    instance.save()
                    messages.success(request, f'Successfully bidded ${bid_price:.2f} for this listing!')
                else:
                    bidder = Bid.objects.get(bidder=request.user.id)
                    bidder_query = Bid.objects.filter(bidder=request.user.id)
                    
                    if bid_price < bidder.bid:
                        messages.error(request, f'Unsuccessful! Bid placed of ${bid_price:.2f} is not higher than current highest bid or starting bid')
                    elif bid_price == bidder.bid:
                        messages.error(request, f'Unable to update current bid, you bidded the same amount as your previous of ${bid_price:.2f}')
                    else:
                        bidder_query.update(bid=bid_price)
                        messages.success(request, f'Successfully updated current bid to ${bid_price:.2f}')
        
        # add listing to watchlist
        elif 'add_to_watchlist' in request.POST:
            item = Listing.objects.get(pk=listing_id)
            user = User.objects.get(pk=request.user.id)
            
            if not User.objects.filter(watchlist=item).exists():
                    user.watchlist.add(item)
                    user.save()
                    messages.success(request, 'Successfully added listing to watchlist')
                    return HttpResponseRedirect(reverse('watchlist'))
            else:
                messages.error(request, 'Listing already exists on watchlist')

    return render(request, "auctions/listing.html", {
        "title": "Listing",
        "listing": listing,
        "bid_form": BidForm(),
    })

# watchlist page
@login_required
def watchlist(request):
    user = User.objects.get(pk=request.user.id)
    watchlist = user.watchlist.all()
    
    if request.method == "POST":
        item_id = request.POST['listing_id']
        try:
            user.watchlist.remove(item_id)
        except:
            messages.error(request, 'Unable to remove from Watchlist')
        
        messages.success(request, 'Successfully removed item from Watchlist')
            
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back {user}!')
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")  

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Successfully logged out.')
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
