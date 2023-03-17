from django.db import transaction

from video_hosting.models import User, WalletUser, Check
from django.db.models import Q
from django.contrib.auth.backends import ModelBackend

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
def send_money(to_user, email, money, username):
    user = User.objects.get(username=username)
    cond = get_wallet(username)
    if user.email == email and float(cond) >= float(money) and User.objects.filter(username=to_user).exists():
        wall = WalletUser.objects.get(user_id=user.id)
        wall.condition -= float(money)
        user_to = User.objects.get(username=to_user)
        wall_to = WalletUser.objects.get(user_id=user_to.id)
        wall_to.condition += float(money)
        wall.save()
        wall_to.save()
        return True
    else:
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