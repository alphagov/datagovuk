from django.conf import settings
from django.urls import path

from datagovuk.core.feature_flags import flag_required

from . import views

app_name = "support"

urlpatterns = [
    path(
        "support-form/",
        flag_required(settings.FEATURE_FLAGS.SUPPORT_FORM, views.SupportFormView.as_view()),
        name="support-form",
    ),
]
