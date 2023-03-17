from django import forms
from django.forms import Textarea
from .models import Video, Comments, User, Profile
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ('description', 'image', 'file')
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            
class AuthUserForm(AuthenticationForm, forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password',)
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            self.fields['username'].widget.input_text = "change"




class RegisterUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password','email', 'phone')
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
        
        
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ('text',)
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['text'].widget = Textarea(attrs={'rows':5}) 
        
        
class EditeProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        
