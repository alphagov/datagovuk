from django.urls import reverse


def test_version(page, live_server_url, settings):
    settings.DATAGOVUK_GIT_SHA = "my-test-sha"
    page.goto(live_server_url + reverse("core:version"))
    assert settings.DATAGOVUK_GIT_SHA in page.content()
