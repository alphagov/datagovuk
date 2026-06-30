def publisher(request):
    publisher = request.publisher if request.publisher else None
    return {
        "publisher": publisher,
    }
