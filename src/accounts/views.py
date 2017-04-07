from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.contrib import messages, auth

from accounts.models import Token

# Create your views here.
def send_login_email(request):
    email = request.POST['email']
    token = Token.objects.create(email=email)
    url = request.build_absolute_uri(
        reverse('login') + '?token=' + str(token.uid)
    )
    message_body = f'Use this link to login:\n\n{url}'
    send_mail(
        'Your login link for tdd',
        message_body,
        'noreply@lttviet.com',
        [email]
    )
    messages.success(
        request,
        "Check your email, we've sent you a link you can use to login"
    )
    return redirect('/')

def login(request):
    user = auth.authenticate(uid=request.GET.get('token'))
    if user:
        auth.login(request, user)
    return redirect('/')
