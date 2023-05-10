from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from directs.models import Message
from video_hosting.models import User
from django.core.paginator import Paginator
from django.db.models import Q


@login_required
def inbox(request):
    user = request.user
    messages = Message.get_message(user=request.user)
    active_direct = None
    directs = None
    
    if messages:
        message = messages[0]
        active_direct = message['user'].username
        directs = Message.objects.filter(user=user, reciepient=message['user'])
        directs.update(is_read=True)
        
        for message in messages:
            if message['user'].username == active_direct:
                message['unread'] = 0
               
        context = {
            'directs': directs,
            'active_direct': active_direct,
            'messages': messages,
        }
            
        return render(request, 'directs/inbox.html', context)      
   
def Directs(request, username):
    user = request.user
    messages = Message.get_message(user=user)
    active_direct = username
    directs = Message.objects.filter(user=user, reciepient__username=username)
    directs.update(is_read=True)
    
    for message in messages:
        if message['user'].username == username:
            message['unread'] = 0
            
    context = {
            'directs': directs,
            'active_direct': active_direct,
            'messages': messages,
        }
          
    return render(request, 'directs/direct.html', context)      
    
    
def SendMessage(request):
    from_user = request.user
    to_user_username = request.POST.get('to_user')
    body = request.POST.get('body')
    
    if request.method == "POST":
        if body == '':
            return redirect('message')
        elif from_user == to_user_username:
            
            return redirect('message')
        else:
            
            to_user = User.objects.get(username=to_user_username)
            if to_user == from_user:
                
                return redirect('message')
            Message.send_message(from_user, to_user, body)
            return redirect('message')
    else:
        pass
        
def UserSearch(request):
    query = request.GET.get('q')
    context = {}
    if query:
        users = User.objects.filter(Q(username__icontains=query))
        
        paginator = Paginator(users, 8)
        page_number = request.GET.get('page')
        users_paginator = paginator.get_page(page_number)
        
        context = {
            'users': users_paginator,
        }
        
    return render(request, 'directs/search.html', context) 