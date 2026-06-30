from .models import Publisher


class PublisherMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.publisher = None
        if not request.user.is_authenticated:
            return self.get_response(request)

        allowed_publisher_ids = request.user.publishers.all().values_list("id", flat=True)
        user_has_publisher = len(allowed_publisher_ids) > 0
        if not user_has_publisher:
            return self.get_response(request)

        selected_publisher_id = request.session.get("publisher")
        if not selected_publisher_id:
            request.session["publisher"] = allowed_publisher_ids[0]
            selected_publisher_id = request.session["publisher"]

        if selected_publisher_id not in allowed_publisher_ids:
            request.session["publisher"] = None
            return self.get_response(request)

        request.publisher = Publisher.objects.get(id=selected_publisher_id)
        return self.get_response(request)
