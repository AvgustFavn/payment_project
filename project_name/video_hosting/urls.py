from django.urls import path
from . import views


urlpatterns = [
    path('stream/<int:pk>/', views.get_streaming_video, name='stream'),
    path('checks_path/', views.getting_checks),
    path('send_money/', views.send_coins_page),
    path('success/<str:status>', views.status_sending),
    path('error/<str:status>', views.error_wallet),
    path('<int:pk>/', views.VideoDetailView.as_view(), name='videomain'),
    path('', views.get_list_video, name='home'),
    path('profile/<username>/', views.Profile, name="profile"),
    path('profile/<username>/follow/<option>', views.follow, name="follow"),
    path('profile/<username>/wallet/', views.wallet_user),
    path('user/<username>', views.ViewProfile, name='edit'),
    path('edit/<int:pk>/', views.Edite.as_view(), name='edit_profile'),
    path('create/', views.VideoCreateView.as_view(), name='create'),
    path('update/<int:pk>', views.UpdateCreateView.as_view(), name='update'),
    path('delete/<int:pk>', views.DelDeleteView.as_view(), name='delete'),
    path('login/', views.MyprojectLoginView.as_view(), name='login'),
    path('register/', views.RegisterUserView.as_view(), name='register'),
    path('logout/', views.MyprojectLogoutView.as_view(), name='logout'),
    path('video/<int:pk>/like/', views.AddLike.as_view(), name='like'),
    path('video/<int:pk>/dislike/', views.AddDislike.as_view(), name='dislike'),
]
