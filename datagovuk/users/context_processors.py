def user(request):
    publisher = None
    user = request.user if request.user.is_authenticated else None
    # TODO: Adjust this when we have a publisher selector..
    if user and user.publishers.all().count() > 0:
        publisher = user.publishers.first()
    return {
        "user": user,
        "publisher": publisher,
    }
