from django.urls import path
from .views import *

urlpatterns = [

    path("", ProductListView.as_view()),
    path("detail/<int:pk>/", ProductDetailView.as_view()),

    path("create/", ProductCreateView.as_view()),

    path("update/<int:pk>/", ProductUpdateView.as_view()),

    path("delete/<int:pk>/", ProductDeleteView.as_view()),
     path("add/review/<int:pk>/", AddReviewView.as_view()),
    path("get/review/<int:pk>/", ProductReviewListView.as_view()),
    path("delete/review/<int:review_id>/", DeleteReviewView.as_view()),

]