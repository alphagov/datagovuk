from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

from .forms import HarvestSourceForm, PublisherRegistrationForm
from .mixins import PublisherLoginRequiredMixin
from .models import HarvestSource, Publisher, PublisherMember


class HomeView(PublisherLoginRequiredMixin, TemplateView):
    template_name = "publishing/home.jinja"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["harvester_sources"] = HarvestSource.objects.filter(publisher=self.request.publisher)
        return context


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
        self.request.session["publisher"] = str(instance.id)

        return super().form_valid(form)


class AddHarvestSourceView(PublisherLoginRequiredMixin, CreateView):
    model = HarvestSource
    form_class = HarvestSourceForm
    template_name = "publishing/add_harvest_source.jinja"
    success_url = reverse_lazy("publishing:home")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["publisher"] = self.request.publisher

        return kwargs
