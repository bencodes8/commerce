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
        "title": "Auctions",
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
        
            created_item = Listing.objects.latest('listing_id')
            
            for genres_id in genres:
                created_item.genres.add(genres_id)

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
    # adds item to watchlist
    if request.method == "POST":
        
        user = User.objects.get(pk=request.user.id)
        item = Listing.objects.get(pk=listing_id)
        
        if not User.objects.filter(watchlist=item).exists():
                user.watchlist.add(item)
                user.save()
                messages.success(request, 'Successfully added listing to watchlist')
                return HttpResponseRedirect(reverse('watchlist'))
        else:
            messages.error(request, 'Listing already exists on watchlist')

    return render(request, "auctions/listing.html", {
        "title": "Listing",
        "listing": listing
    })

# bidding page
@login_required
def bid(request, listing_id):
    item = Listing.objects.get(pk=listing_id)
    
    if request.method == "POST":
        bid_form = BidForm(request.POST)
        if bid_form.is_valid():
            instance = bid_form.save(commit=False)
            bid_price = float(request.POST['bid'])
            if bid_price >= item.listing_id:
                instance.bidder = request.user
                instance.listing = item
                instance.bid = bid_price
                instance.save()
        else:
            messages.error(request, 'Bid placed is not higher than current placed bids or starting bid. Try again.')
            return render(request, "auctions/bid.html", {
                "bid_form": BidForm(request.POST),
                "item": item
            })
            
    return render(request, "auctions/bid.html", {
        "bid_form": BidForm(),
        "item": item
    })

# watchlist page
@login_required
def watchlist(request):
    user = User.objects.get(pk=request.user.id)
    watchlist = user.watchlist.all()
    
    if request.method == "POST":
        item_id = request.POST.get('listing_id')
        try:
            user.watchlist.remove(item_id)
        except:
            print('no')
            
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
    messages.success('Successfully logged out.')
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
