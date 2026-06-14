from django.views.generic import ListView
from .models import Hotel


class HotelListView(ListView):

    model = Hotel

    template_name = "hotels/hotel_list.html"

    context_object_name = "hotels"

    paginate_by = 9

    def get_queryset(self):
        qs = Hotel.objects.filter(is_active=True)
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(name__icontains=q)
        city = self.request.GET.get("city")
        if city:
            qs = qs.filter(city=city)
        sort = self.request.GET.get("sort")
        if sort == "rating":
            qs = qs.order_by("-rating")
        elif sort == "name":
            qs = qs.order_by("name")
        else:
            qs = qs.order_by("-created_at")
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cities"] = (
            Hotel.objects.filter(is_active=True)
            .values_list("city", flat=True)
            .distinct()
            .order_by("city")
        )
        return context
