import requests
from celery import shared_task

from .models import Catalogue, HarvestRun


def fail_run(harvest_run):
    harvest_run.status = HarvestRun.HarvestStatus.FAILED
    harvest_run.save()


def log_event(harvest_run, verb, object, target="", additional_context=""):
    HarvestRunEvent.objects.create(
        harvest_run=harvest_run,
        verb=verb,
        object=object,
        target=target,
        additional_context=additional_context,
    )


@shared_task
def harvest(catalogue_id):
    catalogue = Catalogue.objects.get(id=catalogue_id)
    harvest_run = HarvestRun.objects.create(
        catalogue=catalogue,
        status=HarvestRun.HarvestStatus.HARVESTING,
    )

    try:
        result = requests.get(catalogue.url)
        result.raise_for_status()
    except Exception as e:
        log_event(
            harvest_run=harvest_run,
            verb="catalogue marked invalid",
            object=catalogue.url,
            additional_context=e.message,
        )
        fail_run(harvest_run)
        return

    harvest_run.catalogue_result = result.text
    harvest_run.status = HarvestRun.HarvestStatus.SUCCEEDED
    harvest_run.save()
