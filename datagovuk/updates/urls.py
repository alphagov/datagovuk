from django.urls import re_path

from .views import UpdateView

app_name = "updates"

urlpatterns = [
    re_path(
        r"^(?P<year>\d{4})/(?P<slug>[a-z0-9-]+)/$",
        UpdateView.as_view(),
        name="post",
    ),
]
