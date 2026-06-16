from django.views.generic import TemplateView
from hotels.models import Hotel

class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            # Evaluate the queryset immediately to catch database errors here
            context["featured_hotels"] = list(Hotel.objects.filter(
                is_active=True
            ).order_by("-created_at")[:6])
        except Exception:
            context["featured_hotels"] = []
        return context