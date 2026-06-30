def user(request):
    user = request.user if request.user.is_authenticated else None
    return {
        "user": user,
    }
