from django.urls import path
from images.views import (image_create, image_details, image_like, image_list,
                          image_ranking)


app_name = 'images'
urlpatterns = [
    path('', image_list, name='list'),
    path('create/', image_create, name='create'),
    path('like/', image_like, name='like'),
    path('ranking', image_ranking, name='ranking'),
    path('details/<int:id>/<slug:slug>/', image_details, name='details')
]
