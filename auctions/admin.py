from django.contrib import admin
from .models import User, Listing, Genre, Bid, Comment

class ListingAdmin(admin.ModelAdmin):
    list_display = ('owner', 'title', 'description', 'starting_bid')

class BidAdmin(admin.ModelAdmin):
    list_display = ('bidder', 'listing', 'bid')
# Register your models here.
admin.site.register(Listing, ListingAdmin)
admin.site.register(User)
admin.site.register(Genre)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment)
