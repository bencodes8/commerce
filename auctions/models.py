from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal

# user model
class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing', blank=True, null=True)
    
    def __str__(self):
        return f"{self.username}"

# This model will fall under the 'category' specification
class Genre(models.Model):
    name = models.CharField(max_length=32, unique=True)
    
    def __str__(self):
        return f"{self.name}"
    

class Listing(models.Model):
    listing_id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=None, related_name="owner")
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=255, verbose_name="Description")
    starting_bid = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Starting Bid", validators=[MinValueValidator(Decimal('0.01'))])
    image = models.ImageField(upload_to='auctions/media', default=None, blank=True, verbose_name="Image (Optional)")
    date = models.DateTimeField(auto_now_add=True)
    genres = models.ManyToManyField(Genre, verbose_name="Genre(s)")
    
    def __str__(self):
        return f"Listing ID: {self.listing_id} listed {self.title}"

class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, default=None)
    bid = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Bid Amount", validators=[MinValueValidator(Decimal('0.01'))], default=0.01)
    
    def __str__(self):
        return f"User:{self.bidder} bids ${self.bid}"

class Comment(models.Model):
    pass
    # commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    # comment = models.CharField(max_length=255, verbose_name="Comment")
    
    # def __str__(self):
    #     return f"User: {self.commenter} comments {self.comment}"