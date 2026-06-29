from django.contrib.auth.models import User
from django.db import models


class Publisher(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    members = models.ManyToManyField(User, through="PublisherMember", related_name="publishers")

    def __str__(self):
        return self.name


class PublisherMember(models.Model):
    class Role(models.TextChoices):
        MEMBER = "MEMBER", "Member"
        ADMIN = "ADMIN", "Admin"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    date_joined = models.DateField(auto_now_add=True)
    role = models.CharField(max_length=30, choices=Role.choices)

    def __str__(self):
        return f"{self.publisher.name}:{self.user.email}"
