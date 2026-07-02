import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify


class Publisher(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    members = models.ManyToManyField(User, through="PublisherMember", related_name="publishers")

    def __str__(self):
        return self.name


class PublisherMember(models.Model):
    class Role(models.TextChoices):
        MEMBER = "MEMBER", "Member"
        ADMIN = "ADMIN", "Admin"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    date_joined = models.DateField(auto_now_add=True)
    role = models.CharField(max_length=30, choices=Role.choices)

    def __str__(self):
        return f"{self.publisher.name}:{self.user.email}"


class Catalogue(models.Model):
    class CatalogueType(models.TextChoices):
        DCAT_RDF = "DCAT_RDF", "DCAT RDF"

    class HarvestFrequency(models.TextChoices):
        DAILY = "DAILY", "Daily"
        WEEKLY = "WEEKLY", "Weekly"
        MONTHLY = "MONTHLY", "Monthly"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    created_at = models.DateField(auto_now_add=True)
    url = models.URLField()
    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=210)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    catalogue_type = models.CharField(max_length=30, choices=CatalogueType.choices)
    harvest_frequency = models.CharField(max_length=30, choices=HarvestFrequency.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["publisher_id", "slug"],
                name="unique_publisher_slug",
            ),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def latest_harvest_run(self):
        if self.harvest_run.all().count() > 0:
            return self.harvest_run.all().order_by("-started_at")[0]


class HarvestRun(models.Model):
    class HarvestStatus(models.TextChoices):
        QUEUED = "QUEUED", "Queued"
        HARVESTING = "HARVESTING", "Harvesting"
        SUCCEEDED = "SUCCEEDED", "Succeeded"
        FAILED = "FAILED", "Failed"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(auto_now_add=True)
    catalogue = models.ForeignKey(Catalogue, on_delete=models.CASCADE, related_name="harvest_run")
    status = models.CharField(max_length=30, choices=HarvestStatus.choices)
    catalogue_result = models.TextField()

    @property
    def run_event_counts(self):
        event_counts = self.run_event.all().values("verb").annotate(total_events=models.Count("id"))
        event_count_by_verb = {event_count["verb"]: event_count["total_events"] for event_count in event_counts}
        return event_count_by_verb


class HarvestRunEvent(models.Model):
    class Verb(models.TextChoices):
        CATALOGUE_VALIDATED = "CATALOGUE_VALIDATED", "Catalogue marked valid"
        CATALOGUE_INVALIDATED = "CATALOGUE_INVALIDATED", "Catalogue marked invalid"
        LISTING_CATALOGUED = "LISTING_CATALOGUED", "Listing catalogued"
        LINK_CATALOGUED = "LINK_CATALOGUED", "Link catalogued"
        LINK_VALIDATED = "LINK_VALIDATED", "Link marked valid"
        LINK_INVALIDATED = "LINK_INVALIDATED", "Link marked invalid"
        LINK_ORPHANED = "LINK_ORPHANED", "Link marked orphan"

    # TODO: The modelling here is very much not ideal by using charfields where we should use generic relations...
    #   but it's a prototype..
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    harvest_run = models.ForeignKey(HarvestRun, on_delete=models.CASCADE, related_name="run_event")
    verb = models.CharField(max_length=50, choices=Verb.choices)
    object = models.TextField()
    target = models.TextField()
    additional_context = models.TextField()
