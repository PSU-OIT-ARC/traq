from django.conf.urls import patterns, include, url
import views
import projects.views
import tickets.views
import accounts.views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.home),

    # auth
    url(r'^accounts/login/$', 'django_cas.views.login', name='accounts-login'),
    url(r'^accounts/logout/$', 'django_cas.views.logout', name='accounts-logout'),

    # accounts
    url(r'^accounts/profile/$', accounts.views.profile, name='accounts-profile'),

    # projects
    url(r'^projects/create/?$', projects.views.create, name='projects-create'),
    url(r'^projects/?$', projects.views.all, name='projects-all'),
    url(r'^projects/(\d+)/?$', projects.views.detail, name='projects-detail'),

    # tickets
    url(r'^projects/(\d+)/tickets/create/?$', tickets.views.create, name='tickets-create'),
    url(r'^tickets/(\d+)/?$', tickets.views.detail, name='tickets-detail'),
    url(r'^tickets/(\d+)/edit/?$', tickets.views.edit, name='tickets-edit'),
    # comments
    url(r'^comments/(\d+)/edit/?$', tickets.views.comments_edit, name='comments-edit'),
    # work
    url(r'^work/(\d+)/edit/?$', tickets.views.work_edit, name='work-edit'),
    #url(r'^projects/(\d+)/tickets/(\d+)/comments/edit/?$', tickets.views.edit, name='tickets-edit'),
    # Examples:
    # url(r'^$', 'example.views.home', name='home'),
    # url(r'^example/', include('example.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
