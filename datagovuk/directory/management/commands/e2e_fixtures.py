from django.core.management.base import BaseCommand, CommandError

from datagovuk.directory import e2e_fixtures


class Command(BaseCommand):
    help = "Create or delete the E2E test fixtures in Solr"

    def add_arguments(self, parser):
        parser.add_argument("--create", action="store_true", help="Create the E2E fixtures in Solr")
        parser.add_argument("--delete", action="store_true", help="Delete the E2E fixtures from Solr")

    def handle(self, *args, **options):
        if options["create"] == options["delete"]:
            error_message = "Specify exactly one of --create or --delete"
            raise CommandError(error_message)
        if options["create"]:
            e2e_fixtures.create_e2e_fixtures()
            self.stdout.write(self.style.SUCCESS("Created E2E fixtures"))
        else:
            e2e_fixtures.delete_e2e_fixtures()
            self.stdout.write(self.style.SUCCESS("Deleted E2E fixtures"))
