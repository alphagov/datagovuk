from datagovuk.core.context_processors import google_tag_manager


class TestContextProcessors:
    def test_google_tag_manager(self, settings):
        settings.GOOGLE_TAG_MANAGER_ID = "UA-XXXXX-Y"
        settings.GOOGLE_TAG_MANAGER_AUTH = "fake-auth-token"
        settings.GOOGLE_TAG_MANAGER_PREVIEW = "fake-preview-token"

        context = google_tag_manager(request=None)

        assert context["GOOGLE_TAG_MANAGER_ID"] == "UA-XXXXX-Y"
        assert context["GOOGLE_TAG_MANAGER_AUTH"] == "fake-auth-token"
        assert context["GOOGLE_TAG_MANAGER_PREVIEW"] == "fake-preview-token"
