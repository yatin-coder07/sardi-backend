from django.urls import path
from .views import *

urlpatterns = [

    path("", ProductListView.as_view()),

    path("create/", ProductCreateView.as_view()),

    path("update/<int:pk>/", ProductUpdateView.as_view()),

    path("delete/<int:pk>/", ProductDeleteView.as_view()),

]