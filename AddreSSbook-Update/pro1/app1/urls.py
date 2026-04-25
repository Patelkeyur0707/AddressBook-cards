from django.contrib import admin
from django.urls import path, re_path
from app1 import views
from django.views.static import serve
from django.conf import settings

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add/', views.add_contact, name='add'),
    path('list/', views.list_contacts, name='list'),

    path('view/<int:contact_id>/', views.view_contact, name='view'),
    path('edit/<int:contact_id>/', views.edit_contact, name='edit'),
    path('delete/<int:id>/', views.delete_contact, name='delete'),

    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]