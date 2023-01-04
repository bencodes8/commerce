from django.contrib.auth.models import AbstractUser
from django.db import models

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=5, decimal_places=2)
    image = models.URLField()

class Bid(models.Model):
    pass

class Comment(models.Model):
    pass

class User(AbstractUser):
    pass
