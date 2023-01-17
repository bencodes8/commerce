from django.contrib import admin
from .models import User, Listing, Genre

# Register your models here.
admin.site.register(Listing)
admin.site.register(User)
admin.site.register(Genre)