from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$','socialnetwork.views.home',name='home'),
    # Route for built-in authentication with our own custom login page
    url(r'^login$', 'django.contrib.auth.views.login', {'template_name':'socialnetwork/login.html'}, name='login'),
    # Route to logout a user and send them back to the login page
    url(r'^logout$','django.contrib.auth.views.logout_then_login',name='logout'),
    url(r'^register$', 'socialnetwork.views.register', name='register'),
    url(r'^add-post$', 'socialnetwork.views.add_post', name='add_post'),
    url(r'^edit-profile$', 'socialnetwork.views.editprofile', name='edit_profile'),
    url(r'^profile/(?P<user_id>\d+)$', 'socialnetwork.views.profile', name='profile'),
    url(r'^photo/(?P<id>\d+)$', 'socialnetwork.views.get_photo', name='photo'),
    url(r'^followerstream$', 'socialnetwork.views.followerstream', name='followerstream'),
    url(r'^follow/(?P<user_id>\d+$)', 'socialnetwork.views.follow', name='follow'),
    url(r'^unfollow/(?P<user_id>\d+$)', 'socialnetwork.views.unfollow', name='unfollow'),
    url(r'^get-list-json$', 'socialnetwork.views.get_list_json'),
    url(r'^refresh_page$', 'socialnetwork.views.refresh_page'),
    url(r'^add-comment$', 'socialnetwork.views.add_comment', name='add_comment'),
    url(r'^confirm-registration/(?P<username>[a-zA-Z0-9_@\+\-]+)/(?P<token>[a-z0-9\-]+)$', 'socialnetwork.views.confirm_registration', name='confirm'),
)