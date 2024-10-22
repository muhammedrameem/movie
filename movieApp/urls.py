from django.contrib import admin
from django.urls import path
from .import views
urlpatterns = [
       path('',views.home),
       path('register/',views.register, name='register'),
       path('login/',views.login),
       path('dashboard/',views.dashboard),
       path('submit-movie/', views.submit_movie, name='submit_movie'),
       path('movie_list/', views.movie_list, name='movie_list'),
       path('movies/', views.movies, name='movies'),
]