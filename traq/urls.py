from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView

from arcutils.cas import views as cas_views

from . import views

from .projects import views as projects
from .projects.views import components as components
from .projects.views import reports as reports
from .projects.views import milestones as milestones

from .tickets import views as tickets
from .tickets.views import work as work
from .todos import views as todos
from .accounts import views as accounts


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.home),

    # auth
    url(r'^accounts/login/$', cas_views.login, name='accounts-login'),
    url(r'^accounts/logout/$', cas_views.logout, name='accounts-logout'),
    url(r'^accounts/cas/validate/$', cas_views.validate, name='cas-validate'),

    # accounts
    url(r'^accounts/profile/$', accounts.profile, name='accounts-profile'),
    url(r'^accounts/profile/(?P<tickets>\w+)/$', accounts.profile, name='accounts-profile'),
    url(r'^accounts/timesheet/$', accounts.timesheet, name='accounts-timesheet'),

    # projects
    url(r'^projects/create/?$', projects.create, name='projects-create'),
    url(r'^projects/?$', projects.all, name='projects-all'),
    url(r'^projects/(\d+)/?$', projects.detail, name='projects-detail'),
    url(r'^projects/(\d+)/edit/?$', projects.edit, name='projects-edit'),
    url(r'^projects/(\d+)/meta/?$', projects.meta, name='projects-meta'),
    url(r'^projects/(\d+)/edit_sprint/?$', projects.edit_sprint, name='projects-edit-sprint'),
    url(r'^projects/(\d+)/search/?$', projects.search, name='projects-search'),
    
    #scrum
    url(r'^projects/(\d+)/dashboard/?$', projects.scrum.dashboard, name='projects-dashboard'),
    url(r'^projects/(\d+)/scrum/?$', projects.scrum.scrum, name='projects-scrum'),
    url(r'^projects/(\d+)/which_sprint/?$', projects.scrum.which_sprint, name='projects-which-sprint'),
    url(r'^projects/(\d+)/scrum/backlog/?$', projects.scrum.backlog, name='projects-backlog'),
    url(r'^projects/(\d+)/scrum/sprint_planning/?$', projects.scrum.sprint_planning, name='projects-sprint-planning'),
    
    # components
    url(r'^projects/(\d+)/components/create/?$', components.create, name='components-create'),
    url(r'^components/(\d+)/edit/?$', components.edit, name='components-edit'),
    
    # reports
    url(r'^projects/(\d+)/reports/grid/?$', reports.grid, name='projects-reports-grid'),
    url(r'^projects/(\d+)/reports/component/?$', reports.component, name='projects-reports-component'),
    url(r'^projects/(\d+)/reports/invoice/?$', reports.invoice, name='projects-reports-invoice'),
    url(r'^projects/reports/mega/?$', reports.mega, name='projects-reports-mega'),
    url(r'^projects/reports/summary/?$', reports.summary, name='projects-reports-summary'),
    
    # milestones
    url(r'^projects/(\d+)/milestones/create/?$', milestones.create, name='milestones-create'),
    url(r'^milestones/(\d+)/edit/?$', milestones.edit, name='milestones-edit'),
    url(r'^milestones/(\d+)/detail/?$', milestones.detail, name='milestones-detail'),

    # tickets
    url(r'^projects/(\d+)/tickets/create/?$', tickets.create, name='tickets-create'),
    url(r'^tickets/(\d+)/?$', tickets.detail, name='tickets-detail'),
    url(r'^tickets/(\d+)/edit/?$', tickets.edit, name='tickets-edit'),
    url(r'^projects/(\d+)/tickets/bulk/?$', tickets.bulk, name='tickets-bulk'),
    url(r'^projects/(\d+)/tickets/?$', tickets.listing, name='tickets-list'),
    
    #to dos
    url(r'^projects/(\d+)/todos/create/?$', todos.create, name='todos-create'),
    url(r'^projects/(\d+)/todos/?$', todos.listing, name='todos-list'),
    url(r'^todos/(\d+)/?$', todos.detail, name='todos-detail'),
    url(r'^todos/(\d+)/edit/?$', todos.edit, name='todos-edit'),
    url(r'^project/(\d+)/prioritize/?$', todos.prioritize, name='todos-prioritize'),
    url(r'^projects/(\d+)/todos/bulk/?$', todos.bulk, name='todos-bulk'),

    # comments
    url(r'^comments/(\d+)/edit/?$', tickets.comments_edit, name='comments-edit'),
    # work
    url(r'^work/(\d+)/edit/?$', work.edit, name='work-edit'),
    url(r'^tickets/(\d+)/work/create/?$', work.create, name='work-create'),
    url(r'^work/(\d+)/pause/?$', work.pause, name='work-pause'),
    url(r'^work/(\d+)/continue/?$', work.continue_, name='work-continue'),

    # Examples:
    # url(r'^$', 'example.views.home', name='home'),
    # url(r'^example/', include('example.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^cloak/', include('cloak.urls')),
    url(r'^hook/', include('github_hook.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static("htmlcov", document_root="htmlcov", show_indexes=True)
