from django.urls import path
from . import views

urlpatterns = [
    # Homepage view
    path('', views.homepage, name='homepage'),

    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('create-user/', views.create_user, name='create_user'),

    # Tables
    path('tables/', views.table_list, name='table_list'),
    path('tables/new/', views.table_create, name='table_create'),
    path('tables/<int:pk>/edit/', views.table_update, name='table_update'),
    path('tables/<int:pk>/delete/', views.table_delete, name='table_delete'),
    path('tables/grid/', views.table_grid, name='table_grid'),

    # Reservations
    path('reservations/new/', views.reservation_create, name='reservation_create'),
    path('reservations/<int:pk>/edit/', views.reservation_update, name='reservation_update'),
    path('reservations/<int:pk>/delete/', views.reservation_delete, name='reservation_delete'),
] 
