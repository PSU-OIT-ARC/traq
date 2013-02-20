from django.conf.urls import patterns, include, url
import views
import projects.views
import tickets.views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.home),
    url(r'^projects/create/?$', projects.views.create, name='projects-create'),
    url(r'^projects/?$', projects.views.all, name='projects-all'),
    url(r'^projects/(\d+)/?$', projects.views.detail, name='projects-detail'),
    url(r'^projects/(\d+)/tickets/create?$', tickets.views.create, name='tickets-create'),
    url(r'^projects/(\d+)/tickets/(\d+)/?$', tickets.views.detail, name='tickets-detail'),
    # Examples:
    # url(r'^$', 'example.views.home', name='home'),
    # url(r'^example/', include('example.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
