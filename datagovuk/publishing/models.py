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
