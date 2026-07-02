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
    catalogue = models.ForeignKey(Catalogue, on_delete=models.CASCADE)
    status = models.CharField(max_length=30, choices=HarvestStatus.choices)
    catalogue_result = models.TextField()


class HarvestRunEvent(models.Model):
    # TODO: The modelling here is very much not ideal by using charfields where we should use generic relations...
    #   but it's a prototype..
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    harvest_run = models.ForeignKey(HarvestRun, on_delete=models.CASCADE)
    verb = models.CharField(max_length=50)
    object = models.TextField()
    target = models.TextField()
    additional_context = models.TextField()
