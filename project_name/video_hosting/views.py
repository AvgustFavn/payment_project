# -*- coding: utf-8 -*-

from django.http import StreamingHttpResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormMixin
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from .backends import *
from .models import *
from .services import open_file
from .forms import ArticleForm, AuthUserForm, RegisterUserForm, CommentForm, EditeProfileForm
from django.views import View
from django.db import transaction
from .models import Video, FollowersCount

def get_list_video(request):
    video_list = Video.objects.order_by('-likes')[:10]
    
    context = {
        'video_list': video_list
    }

    return render(request, 'video_hosting/home.html', context)
    



def get_streaming_video(request, pk: int):
    file, status_code, content_length, content_range = open_file(request, pk)
    response = StreamingHttpResponse(file, status=status_code, content_type='video/mp4')

    response['Accept-Ranges'] = 'bytes'
    response['Content-Length'] = str(content_length)
    response['Cache-Control'] = 'no-cache'
    response['Content-Range'] = content_range
    return response
    
class CustomSuccessMessageMixin:
    
    @property
    def success_msg(self):
        return False
    
    def form_valid(self,form):
        messages.success(self.request, self.success_msg)
        return super().form_valid(form)
        
    def get_success_url(self):
        return '%s?id=%s' % (self.success_url, self.object.id)
        
        
# view profile
def ViewProfile(request, pk : int):
    user = request.user
    video_list = Video.objects.filter(author=request.user.id)
    context = {
       'user': user,
       'video_list': video_list, 
    }
    if not request.user.is_authenticated:
        return redirect('login')
    else:
    
        return render(request, 'video_hosting/user_profile.html', context)
        
def Profile(request, username):
    video = Video
    current_user = request.GET.get('username')
    logged_in_user = request.user.username
    user = get_object_or_404(User, username=username)
    video_list = Video.objects.filter(author=user.id)
    
    
    # статистика пользователя
    post_count = Video.objects.filter(author=user.id).count()
    following_count = FollowersCount.objects.filter(user=user).count()
    followers_count = FollowersCount.objects.filter(follower=user).count()
    
    follow_status = FollowersCount.objects.filter(follower=user, user=request.user).exists()
    
    context = {
       'user': user,
       'video_list': video_list,
       'current_user': current_user, 
       'logged_in_user' : logged_in_user,
       'post_count' : post_count,
       'following_count' : following_count, 
       'followers_count' : followers_count, 
       'follow_status' : follow_status,
    }
    if not request.user.is_authenticated:
        return redirect('login')
    else:
    
        return render(request, 'video_hosting/profile.html', context)

def wallet_user(request, username):
    user = get_object_or_404(User, username=username)
    try:
        if request.user.username == user.username:
            if request.method == 'GET':
                counts = get_wallet(username)
                return render(request, 'video_hosting/wallet.html', context={'money': counts})
            else:
                code = request.POST.get('code')
                res = end_check(code, request.user.username)
                if res:
                    return redirect('/success/success_payment')
                else:
                    return redirect('/error/code')

        else:
            return redirect(f'/profile/{request.user.username}/wallet/')
    except:
        return redirect('/error/code1')


def send_coins_page(request):
    if request.method == 'GET' and request.user.is_authenticated:
        counts = get_wallet(request.user)
        return render(request, 'video_hosting/sendmoney.html', context={'money': counts})
    elif request.method == 'POST' and request.user.is_authenticated:
        to_user = request.POST.get('to_name', None)
        money = request.POST.get('count', None)
        username = request.user.username
        res = send_money(to_user, money, username)
        if res:
            send_notf(username, to_user, money)
            return redirect('/success/success_send')

        else:
            return redirect('/error/error_send')

    return redirect('/login')
    
def send_stars_page(request):
    if request.method == 'GET' and request.user.is_authenticated:
        counts = get_wallet(request.user)
        return render(request, 'video_hosting/sendstar.html', context={'money': counts})
    elif request.method == 'POST' and request.user.is_authenticated:
        to_user = request.POST.get('to_name', None)
        email = request.POST.get('email', None)
        money = request.POST.get('count', None)
        username = request.user.username
        res = send_money(to_user, email, money, username)
        if res:
            return redirect('/success/success_send')

        else:
            return redirect('/error/error_send')

    return redirect('/login')

def status_sending(request, status):
    if request.user.is_authenticated:
        if status == 'success_send':
            return render(request, 'video_hosting/succec.html',
                          context={'title': 'Успешный перевод', 'descr': 'Вы перевели средства другому пользователю!',
                                   'url': f'/profile/{request.user.username}/wallet'
                                   })
        elif status == 'success_payment':
            return render(request, 'video_hosting/succec.html',
                          context={'title': 'Успешная оплата!', 'descr': 'Вы уже получили средства на свой счет :)!',
                                   'url': f'/profile/{request.user.username}/wallet'
                                   })
        
    return redirect('/error/what')

def error_wallet(request, status):
    if request.user.is_authenticated:
        if status == 'error_send':
            return render(request, 'video_hosting/error.html',
                          context={'descr': 'Данные введенные вами не верны, или у вас не достаточно средств',
                                   'url': f'/profile/{request.user.username}/wallet'
                                   })
        elif status == 'what':
            return render(request, 'video_hosting/error.html',
                          context={'descr': 'Возможно вы потерялись',
                                   'url': '/'
                                   })
        elif status == 'code':
            return render(request, 'video_hosting/error.html',
                          context={'descr': 'Ваш код оплаты был уже введен!',
                                   'url': f'/profile/{request.user.username}/wallet'
                                   })
        elif status == 'code1':
            return render(request, 'video_hosting/error.html',
                          context={'descr': 'Неверный код!',
                                   'url': f'/profile/{request.user.username}/wallet'
                                   })
    return redirect(f'/profile/{request.user.username}/wallet')


@csrf_exempt
def getting_checks(req):
    money = req.POST.get('money')
    check = req.POST.get('check')
    create_check(check, float(money))
    return HttpResponse('Created')

def follow(request, username, option):
    user = request.user
    follower = get_object_or_404(User, username=username)
    if request.user == user.username:
        return HttpResponseRedirect(reverse('profile', args=[username]))
    try:
        f, created = FollowersCount.objects.get_or_create(user=request.user, follower=follower)

        if int(option) == 0:
            f.delete()
        return HttpResponseRedirect(reverse('profile', args=[username]))

    except User.DoesNotExist:
        return HttpResponseRedirect(reverse('profile', args=[username]))
    

# edit profile
class Edite(LoginRequiredMixin, CustomSuccessMessageMixin, UpdateView):
    model = User
    template_name = 'video_hosting/edit_user_profile.html'
    form_class = EditeProfileForm
    success_url = reverse_lazy('create')
    success_msg = 'Запись успешно обновлена'
    
    def get_context_data(self, **kwargs):
            kwargs['update'] = True
            return super().get_context_data(**kwargs)
    
    
    
   
        
    
        
       
        
        
        
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip     

class VideoDetailView(DetailView):
    model = Video
    template_name = 'video_hosting/videomain.html'
    content_object_name = 'post'
    form_class = CommentForm
    success_msg = "Комментарий добавлен"
    
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        ip = get_client_ip(self.request)
        print(ip)
        if IpModel.objects.filter(ip=ip).exists():
            print("ip already present")
            video_id = request.GET.get('video.id')
            print(video_id)
            post = Video.objects.get(pk=video_id)
            post.views.add(IpModel.objects.get(ip=ip))
        else:
            IpModel.objects.create(ip=ip)
            video_id = request.GET.get('video.id')
            post = Video.objects.get(pk=video_id)
            post.views.add(IpModel.objects.get(ip=ip))
        return self.render_to_response(context)
        
        
class VideoDetailView(CustomSuccessMessageMixin, FormMixin, DetailView):
    model = Video
    template_name = 'video_hosting/videomain.html'
    content_object_name = 'video_list'
    form_class = CommentForm
    success_msg = "Комментарий добавлен"
    
    
    
    def get_context_data(self, **kwargs):
        kwargs['video_list'] = Video.objects.all()  
        return super().get_context_data(**kwargs)
       
    def get_success_url(self, **kwargs):
        return reverse_lazy('videomain', kwargs={'pk': self.get_object().id})
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
            
    def form_valid(self,form):
        self.object = form.save(commit=False)
        self.object.article = self.get_object()
        self.object.author = self.request.user
        self.object.save()
        return super().form_valid(form)
     
    
        

class VideoCreateView(LoginRequiredMixin, CustomSuccessMessageMixin, CreateView):
    model = Video
    template_name = 'video_hosting/create.html'
    form_class = ArticleForm
    success_url = reverse_lazy('create')
    success_msg = 'Запись создана'
    def get_context_data(self, **kwargs):
        kwargs['list_video'] = Video.objects.all().order_by('-id')
        return super().get_context_data(**kwargs)
        
    def form_valid(self,form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        Audio.objects.create(audio_path=self.object.audio)
        self.object.save()
        return super().form_valid(form)
    
class UpdateCreateView(LoginRequiredMixin, CustomSuccessMessageMixin, UpdateView):
    model = Video
    template_name = 'video_hosting/create.html'
    form_class = ArticleForm
    success_url = reverse_lazy('create')
    success_msg = 'Запись успешно обновлена'
    def get_context_data(self, **kwargs):
        kwargs['update'] = True
        return super().get_context_data(**kwargs)
        
# class DelDeleteView(LoginRequiredMixin, DeleteView):
#     model = Video
#     template_name = 'video_hosting/create.html'
#     success_url = reverse_lazy('create')
#     success_msg = 'Запись удалена'
#     def post(self, request, *args, **kwargs):
#         messages.success(self.request, self.success_msg)
#         return super().post(request)

def delete_video_v(request, pk: int):
    delete_video(pk)
    return redirect('/create')

def download_video_v(request, pk: int):
    return download_video(pk)


class MyprojectLoginView(LoginView):
    template_name = 'video_hosting/login.html'
    form_class = AuthUserForm
    success_url = reverse_lazy('create')
    def get_success_url(self):
        return self.success_url
    
class RegisterUserView(CreateView):
    model = User
    template_name = 'video_hosting/register.html'
    form_class = RegisterUserForm
    success_url = '/checks_phone' # !!!!!!!!!!!!!!!!!!!!!
    success_msg = 'Пользователь успешно создан'
    
    def form_valid(self, form):
        form_valid = super().form_valid(form)
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        phone = form.cleaned_data["phone"]
        aut_user = authenticate(username=username, password=password)
        login(self.request, aut_user)
        create_wallet(username)
        send_code(username, phone)
        return form_valid
        
@csrf_exempt
def agree_phone(request):
    if request.method == 'POST':
        user = request.user
        print(user)
        code = request.POST.get('code', None)
        phone = request.POST.get('phone', None)
        if code:
            return check_code_phone(user, code, request)
        elif phone:
            change_phone(user, phone)
            return render(request, 'video_hosting/smsphone.html')

    else:
        return render(request, 'video_hosting/smsphone.html')

class MyprojectLogoutView(LogoutView):
    next_page = reverse_lazy('home')
    
class AddLike(LoginRequiredMixin, View):

    def post(self, request, pk, *args, **kwargs):
        post = Video.objects.get(pk=pk)

        is_dislike = False

        for dislike in post.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break


        if is_dislike:
            post.dislikes.remove(request.user)

        is_like = False

        for like in post.likes.all():
            if like == request.user:
                is_like = True
                break

        if not is_like:
            post.likes.add(request.user)

        if is_like:
            post.likes.remove(request.user)

        return HttpResponseRedirect(reverse('videomain', args=[str(pk)]))



class AddDislike(LoginRequiredMixin, View):

    def post(self, request, pk, *args, **kwargs):
        post = Video.objects.get(pk=pk)

        is_like = False

        for like in post.likes.all():
            if like == request.user:
                is_like = True
                break

        if is_like:
            post.likes.remove(request.user)



        is_dislike = False

        for dislike in post.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break

        if not is_dislike:
            post.dislikes.add(request.user)

        if is_dislike:
            post.dislikes.remove(request.user)

        return HttpResponseRedirect(reverse('videomain', args=[str(pk)]))
        




