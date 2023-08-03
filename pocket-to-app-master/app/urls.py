from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),

    # list of players as well as creating a new player
    path('playerspage/', views.playerspage, name='playerspage'),
    
    # individual player stats
    path('playerspage/playerstats/<str:name>', views.playerstats, 
        name='playerstats'),

	# Tournament page (list of tournaments, new tournament button)
    path('tournamentspage/', views.tournamentspage, name='tournamentspage'),

    # individual tournament stats
    path('tournamentspage/tournamentstats/<str:urlname>', views.tournamentstats, 
    	name='tournamentstats'),

    # create tournament (list of available players, launch tournament button)
    path('tournamentspage/createtournamentpage/', views.createtournamentpage, 
        name='createtournamentpage'),

    # A table with each medal and a description of how to achieve it
    path('tournamentspage/medalspage/', views.medalspage, 
        name='medalspage'),

    # A table that contains each season
    path('tournamentspage/seasonspage', views.seasonspage, 
        name='seasonspage'),

    # A table that contains each tournament in a season
    path('tournamentspage/seasonspage/seasonstats/<str:urlname>', 
        views.seasonstats, name='seasonstats'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)