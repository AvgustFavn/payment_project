from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from video_hosting.managers import UserManager
from django.core.validators import RegexValidator
from django.db.models.signals import post_save, post_delete
# import PIL
# from PIL import Image

class User(AbstractBaseUser, PermissionsMixin):
    alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Имя должно быть на латинице.')
    username = models.CharField(_('username'), max_length=255, unique=True, validators=[alphanumeric])
    email = models.EmailField(_('email address'),\
        null=True, blank=True)
    phone = models.CharField(_('Телефон'), max_length=30,\
        null=True, blank=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    avatar = models.ImageField(verbose_name = 'Аватар', null=True, blank=True, upload_to="images/profile/")
    bio=models.TextField(verbose_name = 'О себе', null=True, blank=True)
    facebook = models.CharField(max_length=50, null=True, blank=True)
    twitter = models.CharField(max_length=50, null=True, blank=True)
    instagram = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff'), default=False)

    is_verified = models.BooleanField(_('verified'), default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        unique_together = ('username', 'email', 'phone')
    
class Montaj(models.Model):
    filemod = models.FileField(
        upload_to='video1/',
        validators=[FileExtensionValidator(allowed_extensions=['mp4'])]
    )
    
class IpModel(models.Model):
    ip = models.CharField(max_length=100)
    
    def __str__(self):
        return self.ip

class Video(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authors')
    
    description = models.TextField(verbose_name = 'Добавить подпись',)
    image = models.ImageField(verbose_name = 'Обложка',upload_to='image/')
    file = models.FileField(verbose_name = 'Видео',
        upload_to='video/',
        validators=[FileExtensionValidator(allowed_extensions=['mp4'])]
    )
    audio = models.FileField(verbose_name='Музыка',
        upload_to='audio/',
        validators=[FileExtensionValidator(allowed_extensions=['mp3'])],
        null=True,
        default=None
    )
    create_at = models.DateTimeField(auto_now_add=True)
    
    likes = models.ManyToManyField(User, blank=True, related_name='likes')
    dislikes = models.ManyToManyField(User, blank=True, related_name='dislikes')
    views = models.ManyToManyField(IpModel, related_name="post_views", blank=True)
    def __str__(self):
        return self.title
        
    def total_views(self):
        return self.views.count()
        
class Comments(models.Model):
    article = models.ForeignKey(Video, on_delete = models.CASCADE, verbose_name = 'Автор', blank = True, null = True, related_name='comments_video')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now=True)
    text = models.TextField(verbose_name='Текст комментария')
    status = models.BooleanField(verbose_name='Видимость статьи', default=False)
    

class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    avatar = models.ImageField(verbose_name = 'Аватар', null=True, blank=True, upload_to="images/profile/")
    
    def __str__(self):
        return f'{self.user.username} - Profile'
        
    


def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)

def save_user_profile(sender, instance, **kwargs):

	instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)


class FollowersCount(models.Model):
    user = models.CharField(max_length=100, blank = True, null = True)
    follower = models.CharField(max_length=100, blank = True, null = True)
    
    def __str__(self):
        return self.user

class WalletUser(models.Model):
    user_id = models.IntegerField(null=False)
    condition = models.FloatField(default=0.0, null=False)
    likes = models.ManyToManyField(Video, blank=True, related_name='liky')

class Check(models.Model):
    check_info = models.CharField(max_length=200, null=False)
    status = models.BooleanField(default=False) # Если фолс то юзер еще не вводил данные на сайте
    money = models.IntegerField(null=False)

class Audio(models.Model):
    audio_path = models.CharField(max_length=500, null=False)

class PhoneCodes(models.Model):
    username = models.CharField(max_length=255, null=False)
    phone = models.CharField(max_length=30, null=False)
    code = models.IntegerField(null=False)
    status = models.BooleanField(default=False)

