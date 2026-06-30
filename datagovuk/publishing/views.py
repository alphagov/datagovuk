from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import CreateView

from .forms import CatalogueForm, PublisherRegistrationForm
from .mixins import PublisherLoginRequiredMixin
from .models import Catalogue, Publisher, PublisherMember


class HomeView(PublisherLoginRequiredMixin, TemplateView):
    template_name = "publishing/home.jinja"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["catalogues"] = Catalogue.objects.filter(publisher=self.request.publisher)
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


class AddCatalogueView(PublisherLoginRequiredMixin, CreateView):
    model = Catalogue
    form_class = CatalogueForm
    template_name = "publishing/add_catalogue.jinja"
    success_url = reverse_lazy("publishing:home")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["publisher"] = self.request.publisher

        return kwargs


class CatalogueDetailView(PublisherLoginRequiredMixin, DetailView):
    model = Catalogue
    context_object_name = "catalogue"
    template_name = "publishing/catalogue_detail.jinja"
