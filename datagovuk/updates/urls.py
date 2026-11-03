from django.urls import re_path

from .views import UpdateView

app_name = "updates"

urlpatterns = [
    re_path(
        r"^(?P<date>\d{4}-\d{2}-\d{2})/(?P<slug>[a-z0-9-]+)/$",
        UpdateView.as_view(),
        name="post",
    ),
]
