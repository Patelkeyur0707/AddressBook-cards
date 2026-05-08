from django.contrib import admin
from django.urls import path
from app1 import views

urlpatterns = [

    # AUTH
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # DASHBOARD
    path('dashboard/', views.dashboard, name='dashboard'),

    # CONTACTS
    path('list/', views.contact_list, name='list'),
    path('add/', views.add_contact, name='add'),
    path('view/<int:id>/', views.view_contact, name='view'),
    path('edit/<int:id>/', views.edit_contact, name='edit'),
    path('delete/<int:id>/', views.delete_contact, name='delete'),

    # ADMIN MANAGEMENT
    path('admin-list/', views.admin_list, name='admin_list'),
    path('admin/edit/<int:id>/', views.edit_admin, name='edit_admin'),
    path('admin/delete/<int:id>/', views.delete_admin, name='delete_admin'),
]