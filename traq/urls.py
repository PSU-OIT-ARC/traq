from django.conf.urls import patterns, include, url

import views

import projects.views
import projects.views.scrum
import projects.views.components
import projects.views.reports
import projects.views.milestones

import tickets.views
import tickets.views.work
import todos.views
import accounts.views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.home),

    # auth
    url(r'^accounts/login/$', 'djangocas.views.login', name='accounts-login'),
    url(r'^accounts/logout/$', 'djangocas.views.logout', name='accounts-logout', kwargs={"next_page": "/"}),

    # accounts
    url(r'^accounts/profile/$', accounts.views.profile, name='accounts-profile'),
    url(r'^accounts/profile/(?P<tickets>\w+)/$', accounts.views.profile, name='accounts-profile'),

    # projects
    url(r'^projects/create/?$', projects.views.create, name='projects-create'),
    url(r'^projects/?$', projects.views.all, name='projects-all'),
    url(r'^projects/(\d+)/?$', projects.views.detail, name='projects-detail'),
    url(r'^projects/(\d+)/edit/?$', projects.views.edit, name='projects-edit'),
    url(r'^projects/(\d+)/meta/?$', projects.views.meta, name='projects-meta'),
    url(r'^projects/(\d+)/edit_sprint/?$', projects.views.edit_sprint, name='projects-edit-sprint'),
    
    #scrum
    url(r'^projects/(\d+)/dashboard/?$', projects.views.scrum.dashboard, name='projects-dashboard'),
    url(r'^projects/(\d+)/scrum/?$', projects.views.scrum.scrum, name='projects-scrum'),
    url(r'^projects/(\d+)/which_sprint/?$', projects.views.scrum.which_sprint, name='projects-which-sprint'),
    url(r'^projects/(\d+)/scrum/backlog/?$', projects.views.scrum.backlog, name='projects-backlog'),
    
    # components
    url(r'^projects/(\d+)/components/create/?$', projects.views.components.create, name='components-create'),
    url(r'^components/(\d+)/edit/?$', projects.views.components.edit, name='components-edit'),
    
    # reports
    url(r'^projects/(\d+)/reports/grid/?$', projects.views.reports.grid, name='projects-reports-grid'),
    url(r'^projects/(\d+)/reports/component/?$', projects.views.reports.component, name='projects-reports-component'),
    url(r'^projects/(\d+)/reports/invoice/?$', projects.views.reports.invoice, name='projects-reports-invoice'),
    url(r'^projects/reports/mega/?$', projects.views.reports.mega, name='projects-reports-mega'),
    # milestones
    url(r'^projects/(\d+)/milestons/create/?$', projects.views.milestones.create, name='milestones-create'),
    url(r'^milestones/(\d+)/edit/?$', projects.views.milestones.edit, name='milestones-edit'),

    # tickets
    url(r'^projects/(\d+)/tickets/create/?$', tickets.views.create, name='tickets-create'),
    url(r'^tickets/(\d+)/?$', tickets.views.detail, name='tickets-detail'),
    url(r'^tickets/(\d+)/edit/?$', tickets.views.edit, name='tickets-edit'),
    url(r'^projects/(\d+)/tickets/bulk/?$', tickets.views.bulk, name='tickets-bulk'),
    url(r'^projects/(\d+)/tickets/?$', tickets.views.listing, name='tickets-list'),
    
    #to dos
    url(r'^projects/(\d+)/todos/create/?$', todos.views.create, name='todos-create'),
    url(r'^projects/(\d+)/todos/?$', todos.views.listing, name='todos-list'),
    url(r'^todos/(\d+)/?$', todos.views.detail, name='todos-detail'),
    url(r'^todos/(\d+)/edit/?$', todos.views.edit, name='todos-edit'),
    url(r'^project/(\d+)/prioritize/?$', todos.views.prioritize, name='todos-prioritize'),
    url(r'^projects/(\d+)/todos/bulk/?$', todos.views.bulk, name='todos-bulk'),

    # comments
    url(r'^comments/(\d+)/edit/?$', tickets.views.comments_edit, name='comments-edit'),
    # work
    url(r'^work/(\d+)/edit/?$', tickets.views.work.edit, name='work-edit'),
    url(r'^tickets/(\d+)/work/create/?$', tickets.views.work.create, name='work-create'),
    url(r'^work/(\d+)/pause/?$', tickets.views.work.pause, name='work-pause'),
    url(r'^work/(\d+)/continue/?$', tickets.views.work.continue_, name='work-continue'),

    # Examples:
    # url(r'^$', 'example.views.home', name='home'),
    # url(r'^example/', include('example.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
