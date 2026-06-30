from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

from .forms import PublisherRegistrationForm
from .mixins import PublisherLoginRequiredMixin
from .models import Publisher, PublisherMember


class HomeView(PublisherLoginRequiredMixin, TemplateView):
    template_name = "publishing/home.jinja"


class PublisherRegistrationView(LoginRequiredMixin, CreateView):
    model = Publisher
    form_class = PublisherRegistrationForm
    template_name = "publishing/registration.jinja"
    success_url = reverse_lazy("publishing:home")

    def form_valid(self, form):
        instance = form.save()
        membership = PublisherMember(
            user=self.request.user,
            publisher=instance,
            role=PublisherMember.Role.ADMIN,
        )
        membership.save()
        self.request.session["publisher"] = instance.id

        return super().form_valid(form)
