from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect


class PublisherLoginRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.publisher:
            return redirect("publishing:register")
        return super().dispatch(request, *args, **kwargs)
