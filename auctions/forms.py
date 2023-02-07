from django import forms

from .models import Listing, Bid, Comment

class NewListingForm(forms.ModelForm):
    class Meta: 
        model = Listing
        fields = ['title', 'description', 'starting_bid', 'image', 'genres']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'starting_bid': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'genres': forms.SelectMultiple(attrs={'class': 'form-select form-select-sm',
                                                  'required': True})  
        }
        
class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['bid']
        widgets = {
            'bid': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Insert Bid Amount Here', 'autofocus': True})
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
        widgets =  {
            'comment': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Comment'})
        }
        labels = {
            'comment': ''
        }