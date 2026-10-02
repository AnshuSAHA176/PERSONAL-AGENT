# urls.py

from django.urls import path

from .views import (
    NightlySessionListView,
    NightlySessionDetailView,
    SessionDiscoveryListView,
    DiscoveryListView,
    TriggerNightlyBrainView,
    BriefingListView
)

urlpatterns = [
    path(
        "",
        BriefingListView.as_view(),
        name="briefing-list"
    ),
    path(
        "sessions/",
        NightlySessionListView.as_view(),
        name="nightly-session-list",
    ),
    path(
        "sessions/<int:pk>/",
        NightlySessionDetailView.as_view(),
        name="nightly-session-detail",
    ),
    path(
        "sessions/<int:session_id>/discoveries/",
        SessionDiscoveryListView.as_view(),
        name="session-discoveries",
    ),
    path(
        "discoveries/",
        DiscoveryListView.as_view(),
        name="discovery-list",
    ),
    path(
        "run/",
        TriggerNightlyBrainView.as_view(),
        name="nightly-run",
    ),
]