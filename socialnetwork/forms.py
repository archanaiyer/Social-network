from django import forms

from django.contrib.auth.models import User
from models import *
MAX_UPLOAD_SIZE = 2500000

class RegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=20)
    last_name  = forms.CharField(max_length=20)
    username   = forms.CharField(max_length = 20)
    email      = forms.EmailField(max_length = 100)
    password1  = forms.CharField(max_length = 200, 
                                 label='Password', 
                                 widget = forms.PasswordInput())
    password2  = forms.CharField(max_length = 200, 
                                 label='Confirm password',  
                                 widget = forms.PasswordInput())


    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super(RegistrationForm, self).clean()

        # Confirms that the two password fields match
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.")

        # We must return the cleaned data we got from our parent.
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # TODO: Confirms that the username is not already present in the
        # User model database.
        # if User.objects.filter(email__exact=email):
        #     raise forms.ValidationError("Email is already taken.")
        return email 

    # Customizes form validation for the username field.
    def clean_username(self):
        # Confirms that the username is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        # We must return the cleaned data we got from the cleaned_data
        # dictionary
        return username

class EditProfile(forms.ModelForm):
    class Meta:
        model= Profile
        exclude = (
            'user','content_type','followusers','email','picture_url')

        def clean(self):
            # Calls our parent (forms.Form) .clean function, gets a dictionary
            # of cleaned data as a result
            cleaned_data = super(EditProfile, self).clean()

            #check age
            age= cleaned_data.get('age')
            bio = cleaned_data.get('bio')
            if age<0:
                raise forms.ValidationError("Enter positive age")
            if len(bio)>430:
                raise forms.ValidationError("Maximum size of bio is 430 characters")
            return cleaned_data

        def clean_picture(self):
            picture = self.cleaned_data['picture']
            if not picture:
                return None
            if not picture.content_type or not picture.content_type.startswith('image'):
                raise profile_forms.ValidationError('File type is not image')
            if picture.size > MAX_UPLOAD_SIZE:
                raise profile_forms.ValidationError('File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
            return picture
    picture=forms.FileField(required=False)
        


class EditRegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=20)
    last_name  = forms.CharField(max_length=20)

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super(EditRegistrationForm, self).clean()
        return cleaned_data

class AddPostForm(forms.ModelForm):
    class Meta:
        model = Posts
        exclude = ('user', 'date_time')

        def clean(self):
            cleaned_data = super(AddPostForm, self).clean()
            post_content = cleaned_data.get('post_content')
            if len(post_content)>160:
                raise forms.ValidationError("Maximum size of post is 160 characters")
            return cleaned_data
            