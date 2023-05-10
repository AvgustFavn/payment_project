import os
import random
import time
import glob
from django.db import transaction, connection
from django.http import FileResponse
from django.shortcuts import redirect, render

from directs.models import Message
from project_name.settings import BASE_DIR
from .models import *
from django.db.models import Q
from django.contrib.auth.backends import ModelBackend
from video_hosting import notisend
from moviepy.editor import *
import subprocess

project = 'test_name'  # Имя проекта
api_key = 'db1716d1afe906ae2dee1e4365b2dcc3'  # API-ключ

# Создаём объект
sms = notisend.SMS(project, api_key)


class AuthBackend(object):
    supports_object_permissions = True
    supports_anonymous_user = False
    supports_inactive_user = False

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def authenticate(self, request, username, password):

        try:
            user = User.objects.get(
                Q(username=username) | Q(email=username) | Q(phone=username)
            )

        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user

        else:
            return None


def create_wallet(username):
    user = User.objects.get(username=username)
    WalletUser.objects.create(user_id=user.id)
    user.save()


def get_wallet(username):
    user = User.objects.get(username=username)
    wall = WalletUser.objects.get(user_id=user.id)
    return wall.condition


@transaction.atomic
def send_money(to_user, money, username):
    user = User.objects.get(username=username)
    cond = get_wallet(username)
    if float(cond) >= float(money) and User.objects.filter(username=to_user).exists():
        wall = WalletUser.objects.get(user_id=user.id)
        wall.condition -= float(money)
        user_to = User.objects.get(username=to_user)
        wall_to = WalletUser.objects.get(user_id=user_to.id)
        wall_to.condition += float(money)
        if wall == wall_to:
            print('перевести себе не получится')
            return False
        else:
            wall.save()
            wall_to.save()
            return True

    else:
        print('перевести себе не получится')
        return False


def create_check(check, money):
    check = Check.objects.create(check_info=check, money=money)
    check.save()


@transaction.atomic
def end_check(code, username):
    check = Check.objects.get(check_info=code)
    if not check.status:
        user = User.objects.get(username=username)
        wall = WalletUser.objects.get(user_id=user.id)
        check.status = True
        wall.condition += check.money
        check.save()
        wall.save()
        return True
    else:
        return False


def delete_video(id):
    v = Video.objects.get(id=id)
    os.remove(f'{BASE_DIR}/media/{str(v.file)}')
    with connection.cursor() as cursor:
        cursor.execute(f'DELETE FROM video_hosting_video WHERE id = {id};')


def delete_video_r(id):
    w = VideoCreate.objects.get(id=id)
    os.remove(f'{BASE_DIR}/media/{str(w.file)}')
    with connection.cursor() as cursor:
        cursor.execute(f'DELETE FROM video_hosting_video WHERE id = {id};')


def download_video(id):
    v = Video.objects.get(id=id)
    return FileResponse(open(f'media/{str(v.file)}', 'rb'))


def download_video1(id):
    w = VideoCreate.objects.get(id=id)
    return FileResponse(open(f'media/{str(w.file)}', 'rb'))


def send_notf(from_u, to_u, count):
    from_u = User.objects.get(username=from_u)
    to_u = User.objects.get(username=to_u)
    admin = User.objects.get(username='hello')  # Переименуйте на того, кто будет присылать оповещения
    s_1 = f'{to_u} получил ваш подарок, {count} монет!'
    s_2 = f'{from_u} прислал вам подарок, {count} монет!'
    Message.objects.create(user=from_u, sender=admin, reciepient=from_u, body=s_1)
    Message.objects.create(user=to_u, sender=admin, reciepient=to_u, body=s_2)


def send_code(username, phone):
    code = random.randint(1000, 9999)
    phone = f'7{phone[1:]}'
    print(phone)
    sms.sendSMS(phone, f'Ваш код для подтверждения телефона: {code}')
    PhoneCodes.objects.create(username=username, phone=phone, code=code)


def check_code_phone(username, code, request):
    res = PhoneCodes.objects.get(code=code)
    u = User.objects.get(username=username)
    if str(username) == str(res.username) and res.status == False:
        res.status = True
        u.is_verified = True
        res.save()
        u.save()
        return redirect('/create')
    else:
        return render(request, 'video_hosting/smsphone.html', context={'bad': True})


def change_phone(username, phone):
    u = User.objects.get(username=username)
    u.phone = f'7{phone[1:]}'
    u.save()
    send_code(username, phone)


def add_music(audio_path, video_path):
    video_clip = VideoFileClip(f'{BASE_DIR}/media/{video_path}')
    audio_clip = AudioFileClip(f'{BASE_DIR}/media/{audio_path}')
    video_clip = video_clip.volumex(0.001)
    end = video_clip.duration
    audio_clip = audio_clip.subclip(0, end)
    audio_clip = audio_clip.fx(afx.audio_fadein, 0)
    audio_clip = audio_clip.fx(afx.audio_fadeout, 3)
    if video_clip.audio:  # Если есть аудио в видео
        audio_clip = CompositeAudioClip([video_clip.audio, audio_clip])
    final_clip = video_clip.set_audio(audio_clip)
    new_name = str(video_path).split('video1/')
    old_name = new_name[1]
    new_name = old_name.split('.')
    new_name = f'_{new_name[0]}.{new_name[1]}'
    final_clip = final_clip.resize((1080, 1920))
    final_clip.write_videofile(f'{BASE_DIR}/media/video1/{new_name}', logger="bar", fps=30, bitrate="20000k",
                               threads=20)
    change_video(old_name)


def change_video(old_name):
    video_obj = VideoCreate.objects.get(file=f'video1/{old_name}')
    video_obj.file = f'video1/_{old_name}'
    # os.remove(f'{BASE_DIR}/media/video1/{old_name}')
    video_obj.save()


def audio_dec(function_to_decorate):
    def wrap(self, form):
        resp = function_to_decorate(self, form)
        if self.object.audio:
            add_music(self.object.audio, self.object.file)
        return resp

    return wrap


def video_quality(video_path): # sudo apt-get install ffmpeg
    file_path = f'{BASE_DIR}/media/{video_path}'
    cmd = 'ffprobe -v error -select_streams v:0 -show_entries stream=width,height,bit_rate -of default=noprint_wrappers=1 "{}"'.format(file_path)
    output = subprocess.check_output(cmd, shell=True).decode('utf-8')
    width, height = None, None
    for line in output.split('\n'):
        if 'width' in line:
            width = int(line.split('=')[1])
        elif 'height' in line:
            height = int(line.split('=')[1])

    if height > 1080 or width > 1920:
        os.rename(file_path, f'{BASE_DIR}/media/video/видео2222332.mp4')
        cmd = 'ffmpeg -y -i "{}" -vf scale=-1:1080 -c:a copy "{}"'.format(f'{BASE_DIR}/media/video/видео2222332.mp4', file_path)
        subprocess.call(cmd, shell=True)
        os.remove(f'{BASE_DIR}/media/video/видео2222332.mp4')

    return None
