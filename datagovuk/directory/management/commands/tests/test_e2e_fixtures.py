from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError


@pytest.fixture
def e2e_fixture_functions():
    with (
        patch("datagovuk.directory.e2e_fixtures.create_e2e_fixtures") as create,
        patch("datagovuk.directory.e2e_fixtures.delete_e2e_fixtures") as delete,
    ):
        yield create, delete


def test_e2e_fixtures_create_option_calls_create_e2e_fixtures(e2e_fixture_functions):
    create, delete = e2e_fixture_functions

    call_command("e2e_fixtures", "--create")

    create.assert_called_once_with()
    delete.assert_not_called()


def test_e2e_fixtures_delete_option_calls_delete_e2e_fixtures(e2e_fixture_functions):
    create, delete = e2e_fixture_functions

    call_command("e2e_fixtures", "--delete")

    delete.assert_called_once_with()
    create.assert_not_called()


def test_e2e_fixtures_without_option_raises_command_error():
    with pytest.raises(CommandError, match="Specify exactly one of --create or --delete"):
        call_command("e2e_fixtures")


def test_e2e_fixtures_with_both_options_raises_command_error():
    with pytest.raises(CommandError, match="Specify exactly one of --create or --delete"):
        call_command("e2e_fixtures", "--create", "--delete")
