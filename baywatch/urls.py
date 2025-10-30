from django.contrib import admin
from django.urls import path
from dashboard.views import (
    dashboard,
    full_map,
    events,
    cleanup_by_school,
    ai_chat,
    your_school,
    school_admin,
    event_page,
)
from authentication.views import signup_view, login_view, logout_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", dashboard, name="dashboard"),
    path("full-map/", full_map, name="full_map"),
    path("events/", events, name="events"),
    path("cleanup-progress/", cleanup_by_school, name="cleanup_by_school"),
    path("ai-chat", ai_chat, name="ai_chat"),
    path("your-school/", your_school, name="your_school"),
    path("school-admin/<str:active_tab>", school_admin, name="school_admin"),
    path("signup/", signup_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("event/<int:event_id>", event_page, name="event_page"),
]
