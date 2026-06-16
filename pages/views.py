from django.views.generic import TemplateView
from hotels.models import Hotel

class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured_hotels"] = []
        return context