from django.urls import path

from . import views

urlpatterns = [
    path('', views.moments_list, name='moments_list'),
    path('moments/add/', views.Moment_form, name='moment_create'),
    path('moments/<int:moment_id>/', views.moment_detail, name='moment_detail'),
    path('comix/', views.comic_story, name='comic_story'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('bucket/', views.bucket_list, name='bucket_list'),
    path('bucket/add/', views.add_bucket_item, name='add_bucket_item'),
    path(
        'bucket/<int:item_id>/toggle/',
        views.toggle_bucket_item,
        name='toggle_bucket_item',
    ),
    path('random-moment/', views.random_moment, name='random_moment'),
]
