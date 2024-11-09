# from django.urls import path
# from .views import itinerary_view, Login

# urlpatterns = [
#     path('', itinerary_view, name='itinerary'),
#     path('login',Login, name='login'),
# ]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('demo/', views.generate_itinerary, name='demo'),
    path('logout/', views.logout_view, name='logout'), 
    path('itinerary/', views.itinerary, name='itinerary'),
    path('agra/', views.agra, name='agra'),
    path('amristar/', views.amristar, name='amristar'),
    path('andamanislands/', views.andamanislands, name='andamanislands'),
    path('goa/', views.goa, name='goa'),
    path('kullu/', views.kullu, name='kullu'),
    path('pondicherry/', views.pondicherry, name='pondicherry'),
    path('chat_response/', views.chat_response, name='chat_response')  # Add this lin
]