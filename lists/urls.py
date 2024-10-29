from django.urls import path

from . import views

app_name = 'lists'
urlpatterns = [
    path('', views.index, name='index'),
    path('add', views.add_list, name='add_list'),
    path('<int:list_id>/delete', views.delete_list, name='delete_list'),
    path('<int:list_id>/add_item', views.add_item, name='add_item'),
    path('items/<int:item_id>', views.delete_item, name='delete_item'),
    path('items/<int:item_id>/complete', views.mark_item_complete, name='complete_item'),
]
