def user(request):
    return {
        "user": request.user if request.user.is_authenticated else None,
    }
