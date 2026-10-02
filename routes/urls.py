from django.urls import path

from routes.views import (
    RouteOptimizationView,
)


urlpatterns = [
    path(
        "optimize/",
        RouteOptimizationView.as_view(),
        name="route-optimize",
    ),
]