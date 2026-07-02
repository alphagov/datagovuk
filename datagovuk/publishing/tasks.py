import requests
from celery import shared_task
from django.utils import timezone

from .models import Catalogue, HarvestRun, HarvestRunEvent


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


def log_events_for_catalogue(catalogue_slug, harvest_run):
    if catalogue_slug == "dcat-mock":
        datasets = [
            (
                "http://localhost:8000/mock-catalogue/dcat/dataset-1",
                "Affordability and availability of flood insurance - final report",
            ),
            (
                "http://localhost:8000/mock-catalogue/dcat/dataset-2",
                "Animal Reporting and Movement Service (ARMS) data reports on total number of deer movements",
            ),
        ]
        for dataset_url, dataset_title in datasets:
            log_event(
                harvest_run=harvest_run,
                verb=HarvestRunEvent.Verb.LISTING_CATALOGUED,
                object=dataset_url,
                additional_context=f"Listing title: {dataset_title}",
            )

        working_links = [
            (
                "http://localhost:8000/mock-catalogue/dcat/dataset-1-resource-1",
                "Affordability and availability of flood insurance - final report",
            ),
            (
                "http://localhost:8000/mock-catalogue/dcat/dataset-2-resource-1",
                "Excel spread sheet for download April to June 2017",
            ),
        ]
        for link_url, link_title in working_links:
            log_event(
                harvest_run=harvest_run,
                verb=HarvestRunEvent.Verb.LINK_CATALOGUED,
                object=link_url,
                additional_context=f"Link title: {link_title}",
            )
            log_event(
                harvest_run=harvest_run,
                verb=HarvestRunEvent.Verb.LINK_VALIDATED,
                object=link_url,
                additional_context=f"Link title: {link_title}",
            )

        broken_links = [
            (
                "http://localhost:8000/mock-catalogue/dcat/dataset-2-resource-2",
                "Excel spread sheet for download January to March 2017",
            ),
        ]
        for link_url, link_title in broken_links:
            log_event(
                harvest_run=harvest_run,
                verb=HarvestRunEvent.Verb.LINK_CATALOGUED,
                object=link_url,
                additional_context=f"Link title: {link_title}",
            )
            log_event(
                harvest_run=harvest_run,
                verb=HarvestRunEvent.Verb.LINK_INVALIDATED,
                object=link_url,
                additional_context=f"Link title: {link_title}",
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
            verb=HarvestRunEvent.Verb.CATALOGUE_INVALIDATED,
            object=catalogue.url,
            additional_context=str(e),
        )
        fail_run(harvest_run)
        return

    log_event(
        harvest_run=harvest_run,
        verb=HarvestRunEvent.Verb.CATALOGUE_VALIDATED,
        object=catalogue.url,
        additional_context=str(e),
    )
    log_events_for_catalogue(catalogue.slug, harvest_run)

    harvest_run.catalogue_result = result.text
    harvest_run.status = HarvestRun.HarvestStatus.SUCCEEDED
    harvest_run.ended_at = timezone.now()
    harvest_run.save()
