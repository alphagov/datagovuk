from datagovuk.support.forms import SupportForm


class TestSupportForm:
    def test_valid_form_submission(self):
        form = SupportForm(
            data={
                "http_referer": "https://example.com/test-page",
                "details": "about /test page",
                "name": "Test user",
                "email": "test@example.com",
            },
        )
        assert form.is_valid()
        assert form.cleaned_data["details"] == "about /test page"
        assert form.cleaned_data["http_referer"] == "https://example.com/test-page"
        assert form.cleaned_data["name"] == "Test user"
        assert form.cleaned_data["email"] == "test@example.com"

    def test_invalid_form_submission_for_details_missing(self):
        form = SupportForm(
            data={
                "http_referer": "https://example.com/test-page",
                "details": "",
                "name": "Test user",
                "email": "test@example.com",
            },
        )
        assert not form.is_valid()
        assert "details" in form.errors

    def test_non_required_fields_allowed_with_form_submission(self):
        form = SupportForm(
            data={
                "details": "Test details",
                "name": "",
                "email": "",
            },
        )
        assert form.is_valid()
        assert form.cleaned_data["name"] == ""
        assert form.cleaned_data["email"] == ""
        assert form.cleaned_data["details"] == "Test details"

    def test_form_validation_failed_when_details_have_more_than_max_length(self):
        max_length = 1200
        details = "*" * (max_length + 1)

        form = SupportForm(
            data={
                "details": details,
                "name": "Test user",
                "email": "test@example.com",
            },
        )
        assert not form.is_valid()
        assert "details" in form.errors

    def test_form_submission_http_referer_field_not_required(self):
        form = SupportForm(
            data={
                "details": "Test details",
                "name": "Test user",
                "email": "test@example.com",
            },
        )
        assert form.is_valid()
        assert form.cleaned_data["http_referer"] == ""

    def test_invalid_form_submission_email_is_invalid(self):
        form = SupportForm(
            data={
                "details": "Test details",
                "name": "Test user",
                "email": "test",
            },
        )
        assert not form.is_valid()
        assert "email" in form.errors

    def test_valid_form_submission_details_at_max_length_is_valid(self):
        form = SupportForm(
            data={
                "details": "*" * 1200,
                "name": "Test user",
                "email": "test@example.com",
            },
        )
        assert form.is_valid()
