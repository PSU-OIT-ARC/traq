from django.conf.urls import patterns, include, url
import views
import projects.views
import projects.views.components
import projects.views.reports
import tickets.views
import accounts.views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

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
    url(r'^projects/(\d+)/edit/?$', projects.views.edit, name='projects-edit'),
    # components
    url(r'^projects/(\d+)/components/create/?$', projects.views.components.create, name='components-create'),
    url(r'^components/(\d+)/edit/?$', projects.views.components.edit, name='components-edit'),
    # reports
    url(r'^projects/(\d+)/reports/grid/?$', projects.views.reports.grid, name='projects-reports-grid'),
    url(r'^projects/(\d+)/reports/component/?$', projects.views.reports.component, name='projects-reports-component'),
    url(r'^projects/(\d+)/reports/invoice/?$', projects.views.reports.invoice, name='projects-reports-invoice'),

    # tickets
    url(r'^projects/(\d+)/tickets/create/?$', tickets.views.create, name='tickets-create'),
    url(r'^tickets/(\d+)/?$', tickets.views.detail, name='tickets-detail'),
    url(r'^tickets/(\d+)/edit/?$', tickets.views.edit, name='tickets-edit'),
    # comments
    url(r'^comments/(\d+)/edit/?$', tickets.views.comments_edit, name='comments-edit'),
    # work
    url(r'^work/(\d+)/edit/?$', tickets.views.work_edit, name='work-edit'),
    url(r'^tickets/(\d+)/work/create/?$', tickets.views.work_create, name='work-create'),
    url(r'^work/(\d+)/pause/?$', tickets.views.work_pause, name='work-pause'),
    url(r'^work/(\d+)/continue/?$', tickets.views.work_continue, name='work-continue'),

    # Examples:
    # url(r'^$', 'example.views.home', name='home'),
    # url(r'^example/', include('example.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
