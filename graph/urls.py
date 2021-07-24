from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('accounts/index',views.indexView.as_view(), name='index'),
    path('accounts/index/delete/(?P<id>[0-9]+)/$',views.indexView.delete_dashboard, name='delete_dashboard'),
    # path('accounts/index/add_dashboard',views.indexView.Add_Dashboard, name='Add_Dashboard'),
    path('accounts/dashboard',views.dashboardView.as_view(), name='dashboard'),
    path('accounts/dashboard/delete/(?P<id>[0-9]+)/$',views.dashboardView.delete_panel, name='delete_panel'),
    path('accounts/login', auth_views.LoginView.as_view(template_name="accounts/login.html"), name='login'),
    path('account/logout', auth_views.LogoutView.as_view(), name='logout'),
    # path('accounts/dashboard/addPanel/', views.addPanel, name='addPanel'),
    path('accounts/settings',views.settingsView.as_view(), name='settings'),
    path('accounts/settings/configuration',views.configurationView.as_view(), name='configuration'),
    path('accounts/settings/configuration/delete/(?P<id>[0-9]+)/$',views.configurationView.delete_datasource, name='delete_datasource'),
    path('accounts/settings/configuration/add_datasource/', views.Add_DataSource, name='Add_DataSource'),
    path('accounts/settings/variables',views.variablesView.as_view(), name='variables'),
    path('accounts/settings/variables/delete/(?P<id>[0-9]+)/$',views.variablesView.delete_variable, name='delete_variable'),
    path('chart',views.demo_discretebarchart, name='chart'),
]