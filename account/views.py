from django.core.mail import EmailMessage,send_mail

from django.contrib.auth.models import User
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.core.mail import send_mail
from emailverification import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes,force_str
from .tokens import generate_token
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
# Create your views here.



def home(request):
    return render(request,'account/index.html')
def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        if User.objects.filter(username=username):
            messages.error(request,'username already exist')
            return redirect('account:home')
        if User.objects.filter(email=email):
            messages.error(request,'email already registered')
            return redirect('account:home')
        new_user = User.objects.create_user(username,email,pass1)
        new_user.first_name = fname
        new_user.last_name = lname
        new_user.is_active = False
        new_user.save()
        messages.success(request,"your accunte has been successfuly created")
        #sending email
        subject = 'welcom to gfg'
        message = 'i wish it work and you can read it '+new_user.first_name
        from_email = settings.EMAIL_HOST_USER
        to_list=[new_user.email]
        send_mail(subject,message,from_email,to_list,fail_silently=True)
        #email address confirmation email
        current_site = get_current_site(request)
        email_subject = "confirm your emmail"
        message2 = render_to_string('email_confirmation.html',{
            'name':new_user.first_name,
            'domain':current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(new_user.pk)),
            'token':generate_token.make_token(new_user)
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [new_user.email],
        )
        email.fail_silently = True
        email.send()
        return redirect('account:signin')
    return render(request,'account/signup.html')
def signin(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get("pass1")
        user = authenticate(username=username,password=password)
        if user is not None:
            login(request,user)
            fname = user.first_name
            return render(request,'account/index.html',{'fname':fname})
        else:
            messages.error(request,'there is an mistake')
            return redirect('account:home')
    return render(request,'account/signin.html')
def signout(request):
    logout(request)
    messages.success(request,'loged out seccessfuly')
    return redirect('account:home')
def activate(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None
    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        myuser.save()
        login(request,myuser)
        return redirect('account:home')
    else:
        return render(request,'activation_failed.html')
