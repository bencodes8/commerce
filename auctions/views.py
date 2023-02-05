from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import User, Listing, Bid, Comment
from .forms import NewListingForm, BidForm, SearchForm, CommentForm

# index page
def index(request):
    active_listings = Listing.objects.all()
    return render(request, "auctions/index.html", {
        "listings": active_listings
    })

# inactive listings page
def inactive(request):
    inactive_listings = Listing.objects.filter(status=False)
    return render(request, "auctions/inactive.html", {
        "listings": inactive_listings
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
        messages.error(request, 'Sorry, directing you to this listing item lead to an error. Perhaps it was deleted?')
    
    if not request.user.is_authenticated:
        return render(request, "auctions/listing.html", {
            'listing': listing,
            'comments': Comment.objects.filter(listing=listing_id)
        })   
    else:
        user = User.objects.get(pk=request.user.id)
        

        if request.method == "POST":
            # bid logic
            if 'bid_amount' in request.POST:
                bid_form = BidForm(request.POST)
                
                if bid_form.is_valid():
                    
                    # keep track of user's bid
                    bid_input = float(request.POST['bid'])
                    
                    # check to see if user's bid is at least higher than starting bid
                    if bid_input >= float(listing.starting_bid):
                        
                        # check if the user has already submitted a bid for this listing or if there are no bids placed yet for this listing
                        if (not Bid.objects.filter(bidder=request.user.id).exists()) or (not Bid.objects.filter(listing=listing_id).exists()):
                            instance = bid_form.save(commit=False)
                            instance.bidder = request.user
                            instance.listing = listing
                            instance.bid = bid_input
                            instance.save()
                            # set the latest bid to the most current
                            if listing.highest_bid is None:
                                listing.highest_bid = Bid.objects.filter(listing=listing_id).latest('bidder')
                                listing.save()
                                
                            messages.success(request, f'Successfully placed ${bid_input:.2f} for this listing!')
                            
                        else:
                            bidder = Bid.objects.filter(bidder=request.user.id).filter(listing=listing_id)     
                            
                            if bid_input < listing.highest_bid.bid:
                                messages.error(request, f'Unsuccessful! Bid placed of ${bid_input:.2f} is not higher than current highest bid' )
                            elif bid_input == listing.highest_bid.bid:
                                messages.error(request, f'Unable to update current bid, the highest bid of ${bid_input:.2f} is the same amount bidded')
                            else:
                                bidder.update(bid=bid_input)
                                listing.save()
                                messages.success(request, f'Successfully updated current bid to ${bid_input:.2f}')
                                return HttpResponseRedirect(reverse('listing', args=[listing.listing_id]))
                    else:
                        messages.error(request, f'Unsuccessful! Bid placed of ${bid_input:.2f} is not equal to or higher than starting bid')   
        
            # add listing to watchlist
            elif 'add_watchlist' in request.POST:
                
                if not User.objects.filter(pk=request.user.id).filter(watchlist=listing).exists():
                        user.watchlist.add(listing)
                        user.save()
                        messages.success(request, 'Successfully added listing to watchlist')
                        return HttpResponseRedirect(reverse('listing', args=[listing.listing_id]))
                else:
                    messages.error(request, 'Listing already exists on watchlist')
         
            # remove listing from watchlist
            elif 'remove_watchlist' in request.POST:
                try: 
                    user.watchlist.remove(listing)
                except:
                    messages.error(request, 'Sorry unable to remove listing from watchlist')
                messages.success(request, 'Successfully removed item from Watchlist')
            
            # close listing
            elif 'close_listing' in request.POST:
               listing.status = False
               listing.save()
        
            # comments
            elif 'comment_send' in request.POST:
                comment = Comment.objects.create(listing=listing, commenter=request.user, comment=request.POST['comment'])
                comment.save()
            
                
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "bid_form": BidForm(),
            "comment_form": CommentForm(),
            "user": user,
            "watchlist": user.watchlist.all(),
            "comments": Comment.objects.filter(listing=listing_id)
        })

# watchlist page
@login_required
def watchlist(request):
    user = User.objects.get(pk=request.user.id)
    watchlist = user.watchlist.all()
            
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist
    })

def search(request):
    return render(request, "auctions/search.html", {
        'search_form': SearchForm()
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
