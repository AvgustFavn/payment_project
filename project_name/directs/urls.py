from django.urls import path
from directs.views import inbox, Directs, SendMessage, UserSearch
from video_hosting.models import User

urlpatterns = [
    path('inbox/', inbox, name='message'),
    
    path('directs/<username>', Directs, name="directs"),
    path('send/', SendMessage, name="send-message"),
    
    path('new/', UserSearch, name="user-search"),
]
