from django.shortcuts import render, redirect, get_object_or_404, HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.template import loader, Context
from django.template.loader import get_template
import json
# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.core import serializers

# Used to generate a one-time-use token to verify a user's email address
from django.contrib.auth.tokens import default_token_generator

# Used to send mail from within Django
from django.core.mail import send_mail

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

# Django transaction system so we can use @transaction.atomic
from django.db import transaction
from socialnetwork.s3 import s3_upload, s3_delete

from socialnetwork.models import *
from socialnetwork.forms import RegistrationForm, EditProfile, EditRegistrationForm, AddPostForm

@login_required
def home(request):
    posts = Posts.objects.all().order_by('-date_time')
    comments = Comment.objects.all()
    addpost_form=AddPostForm(request.POST)
    if (posts):
        finalpost = posts[0]
        profiles = Profile.objects.all()
        context = {'posts' : posts,'finalpost' : finalpost.id, 'comments':comments, 'profiles':profiles, 'addpost_form':addpost_form}
        return render(request, 'socialnetwork/globalstream.html', context)
    profiles = Profile.objects.all()
    context = {'posts' : posts, 'comments':comments, 'profiles':profiles, 'addpost_form':addpost_form}
    return render(request, 'socialnetwork/globalstream.html', context)

def redirect(request):
    return HttpResponseRedirect('socialnetwork')

@login_required
def add_comment(request):
    context={}
    errors=[]
    if not 'commenttext' in request.GET or not request.GET.get('commenttext'):
        errors.append('Enter a comment!')
    else:
        commenttext=request.GET.get('commenttext')
        post_id=request.GET.get('post_id')
        user=User.objects.get(id=request.user.id)
        post_attached_to_user = Posts.objects.get(id=post_id).user
        profile=Profile.objects.get(user=request.user)
        currpost = Posts.objects.get(id=post_id)
        new_comment=Comment()
        new_comment.comment_text=commenttext
        new_comment.comment_datetime=timezone.now()
        new_comment.comment_by=profile
        new_comment.comment_post=currpost
        new_comment.save()
        t = get_template('socialnetwork/commenttemplate.html')
        
        comments = Comment.objects.filter(id=new_comment.id)
        c = Context({'comments': comments})
        rendered = t.render(c)
        response_text = json.dumps({'html': rendered})
        return HttpResponse(response_text, content_type='application/json')
    return HttpResponse("", content_type='application/json')

def get_list_json(request):
    response_text = serializers.serialize('json', Posts.objects.all())
    return HttpResponse(response_text, content_type='application/json')

@login_required
def editprofile(request):
    context={}
    user=request.user
    if request.method == 'GET': 
        #populating it with the values saved in the database
        context['registration_form'] = EditRegistrationForm(initial={'first_name': user.first_name,
        'last_name': user.last_name})
        profile_of_user = User.objects.get(id=user.id)
        userprofileinfo = Profile.objects.get(user=profile_of_user)
        addpost_form = AddPostForm(request.POST)
        context['addpost_form'] = addpost_form
        context['profile_form'] = EditProfile(instance=userprofileinfo)
        return render(request, 'socialnetwork/editprofile.html', context)

    registration = User.objects.get(id=user.id)
    registration_form=EditRegistrationForm(request.POST)
    edit_profile = Profile.objects.get(user=registration)
    profile_form = EditProfile(request.POST, request.FILES, instance=edit_profile)

    if not registration_form.is_valid():
        return render(request, 'socialnetwork/editprofile.html', {'registration_form':registration_form, 'profile_form':profile_form})
  
    registration.first_name=registration_form.cleaned_data['first_name']
    registration.last_name=registration_form.cleaned_data['last_name']
    registration.save()

    if not profile_form.is_valid():
        return render(request, 'socialnetwork/editprofile.html', {'registration_form':registration_form, 'profile_form':profile_form})
    if profile_form.cleaned_data['picture']:
        url = s3_upload(profile_form.cleaned_data['picture'], registration)
        profile=Profile.objects.get(user=request.user)
        profile.picture_url = url

    profile_form.save()
    posts = Posts.objects.all().order_by('date_time').reverse()
    profiles= Profile.objects.all()
    comments = Comment.objects.all()
    addpost_form = AddPostForm(request.POST)
    context['addpost_form']=addpost_form
    context = {'posts' : posts, 'comments':comments, 'profiles':profiles, 'addpost_form':addpost_form}
    return render(request, 'socialnetwork/globalstream.html', context)

@transaction.atomic
def register(request):
    context = {}
    print request.FILES
    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['registration_form'] = RegistrationForm()
        context['profile_form'] = EditProfile()
        return render(request, 'socialnetwork/register.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    registration_form = RegistrationForm(request.POST)
    profile_form = EditProfile(request.POST, request.FILES)

    # Validates the form.
    if not registration_form.is_valid():
        print "reg form not valid"
        return render(request, 'socialnetwork/register.html', {'registration_form':registration_form, 'profile_form':profile_form})

    if not profile_form.is_valid():
        print "profile form not valid"
        return render(request, 'socialnetwork/register.html', {'registration_form':registration_form, 'profile_form':profile_form})

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=registration_form.cleaned_data['username'], 
                                        password=registration_form.cleaned_data['password1'],
                                        first_name=registration_form.cleaned_data['first_name'],
                                        last_name=registration_form.cleaned_data['last_name'],
                                        email=registration_form.cleaned_data['email'])

    # Mark the user as inactive to prevent login before email confirmation.
    new_user.is_active = False
    new_user.save()

    new_profile = Profile()
    new_profile.user = new_user
    new_profile.age=profile_form.cleaned_data['age'] 
    new_profile.bio=profile_form.cleaned_data['bio']

    if profile_form.cleaned_data['picture']:
        url = s3_upload(profile_form.cleaned_data['picture'], new_user.id)
        new_profile.picture_url = url
    new_profile.save()

    # Generate a one-time use token and an email message body
    token = default_token_generator.make_token(new_user)

    email_body = """
Welcome to your Social Network. Please click the link below to
verify your email address and complete the registration of your account:

  http://%s%s
""" % (request.get_host(), 
       reverse('confirm', args=(new_user.username, token)))

    send_mail(subject="Verify your email address",
              message= email_body,
              from_email="abiyer@andrew.cmu.edu",
              recipient_list=[new_user.email])

    context['email'] = registration_form.cleaned_data['email']
    return render(request, 'socialnetwork/needsconfirmation.html', context)

@transaction.atomic
def confirm_registration(request, username, token):
    user = get_object_or_404(User, username=username)

    # Send 404 error if token is invalid
    if not default_token_generator.check_token(user, token):
        raise Http404

    # Otherwise token was valid, activate the user.
    user.is_active = True
    user.save()
    return render(request, 'socialnetwork/confirmed.html', {})

@login_required
@transaction.atomic
def add_post(request):
    errors = []
    context={}
 
    addpost_form = AddPostForm(request.POST)
    context['addpost_form']=addpost_form

    if not addpost_form.is_valid():
        print "Add post form not valid"
        comments = Comment.objects.all()
        posts = Posts.objects.all().order_by('-date_time')
        if (posts):
            finalpost = posts[0]
            profiles = Profile.objects.all()
            context = {'posts' : posts,'finalpost' : finalpost.id, 'comments':comments, 'profiles':profiles, 'addpost_form':addpost_form}
        return render(request, 'socialnetwork/globalstream.html', context)

    if not addpost_form.cleaned_data['post_content']:
        errors.append('Enter a post!')
    else:
        if(len(addpost_form.cleaned_data['post_content'])>160):
            errors.append("It should be less than 160 characters")
        else:
            new_post_user=request.user
            new_post_datetime = timezone.now()
            new_post= Posts(post_content=addpost_form.cleaned_data['post_content'],user=new_post_user,date_time=new_post_datetime)
            new_post.save()

    posts = Posts.objects.all().order_by('date_time').reverse()
    finalpost = posts[0]
    comments = Comment.objects.all()
    profiles = Profile.objects.all()
    context = {'posts' : posts,'errors' :errors,'finalpost' : finalpost.id, 'comments':comments, 'profiles':profiles, 'addpost_form':addpost_form}
    return render(request, 'socialnetwork/globalstream.html', context)

@login_required
def refresh_page(request):
    context={}
    if(request.GET.get('id')):
        finalpost_id=request.GET.get('id')
    else:
        errors.append("Enter a valid input!")
        raise Http404

    posts=Posts.objects.all().filter(id__gt=finalpost_id).order_by('-date_time')
    if (posts):
        finalpost = posts[0]
        t = get_template('socialnetwork/poststemplate.html')
        c = Context({'posts': posts, 'finalpost': finalpost})
        rendered = t.render(c)
        profiles = Profile.objects.all()
        response_text = json.dumps({'html': rendered, 'finalpost':finalpost.id})
        return HttpResponse(response_text, content_type='application/json')

    c = Context({'finalpost': finalpost_id})
    t = get_template('socialnetwork/poststemplate.html')
    rendered = t.render(c)
    response_text = json.dumps({'finalpost':finalpost_id})
    return HttpResponse(response_text, content_type='application/json')

@login_required
def profile(request,user_id):
    errors=[]
    try:
        user=User.objects.get(id=user_id)
        posts=Posts.objects.filter(user=user).order_by('date_time').reverse()
        profile=Profile.objects.get(user=user)
        context = {'user':user,'posts':posts, 'profile':profile, 'current_user':request.user}
        return render(request,'socialnetwork/profile.html',context)
    except ObjectDoesNotExist:
        errors.append('The profile you asked for does not exist.')
        posts = Posts.objects.all().order_by('date_time').reverse()
        profiles = Profile.objects.all()
        comments = Comment.objects.all()
        addpost_form=AddPostForm(request.POST)
        context = {'posts' : posts, 'errors' : errors, 'profiles':profiles, 'comments':comments, 'addpost_form':addpost_form}
        return render(request,'socialnetwork/globalstream.html',context)
    
@login_required
def get_photo(request, id):
    profile = get_object_or_404(Profile, id=id)
    if not profile.picture:
        raise Http404
    return HttpResponse(profile.picture, content_type=profile.content_type)

@login_required
@transaction.atomic
def follow(request,user_id):
    context={}
    errors=[]
    try:
        user=User.objects.get(id=user_id)
        profile=Profile.objects.get(user=user)
        posts=Posts.objects.filter(user=user).order_by('date_time').reverse()
        current_user = request.user
        Profile.objects.get(user=current_user).followusers.add(user)
        current_user.save()
        context = {'user':user,'posts':posts, 'profile':profile,'messages1':"test"}
        return render(request,'socialnetwork/profile.html',context)
    except ObjectDoesNotExist:
        errors.append('You cannot follow this user.')
        posts = Posts.objects.all().order_by('date_time').reverse()
        profiles = Profile.objects.all()
        comments = Comment.objects.all()
        addpost_form=AddPostForm(request.POST)
        context = {'posts' : posts, 'errors' : errors, 'profiles':profiles, 'comments':comments, 'addpost_form':addpost_form}
        return render(request,'socialnetwork/globalstream.html',context)

@login_required
def followerstream(request):
    context = {}
    user=request.user
    posts=Posts.objects.filter(user__in=Profile.objects.get(user=user).followusers.all()).order_by('-date_time')
    context = {'posts' : posts}
    return render(request, 'socialnetwork/followerstream.html', context)
     
@login_required
@transaction.atomic
def unfollow(request,user_id):
    context={}
    errors=[]
    try:
        user=User.objects.get(id=user_id)
        profile=Profile.objects.get(id=user_id)
        posts=Posts.objects.filter(user=user).order_by('date_time').reverse()
        current_user = request.user
        Profile.objects.get(user=current_user).followusers.remove(user)
        current_user.save()
        context = {'user':user,'posts':posts, 'profile':profile, 'messages2':"test"}
        return render(request,'socialnetwork/profile.html',context)
    except ObjectDoesNotExist:
        errors.append('You cannot unfollow this user.')
        posts = Posts.objects.all().order_by('date_time').reverse()
        profiles = Profile.objects.all()
        comments = Comment.objects.all()
        addpost_form=AddPostForm(request.POST)
        context = {'posts' : posts, 'errors' : errors, 'profiles':profiles, 'comments':comments, 'addpost_form':addpost_form}
        return render(request,'socialnetwork/globalstream.html',context)  

