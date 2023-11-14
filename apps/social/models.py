import datetime

from django.contrib.auth.models import User
from django.db import models

from apps.base.models import BaseModel


# Create your models here.
class Friend(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='friend_list')
    friends = models.ManyToManyField(User, symmetrical=True)

    class Meta:
        db_table = "friend"
        ordering = ["-id"]

    def __str__(self):
        return f"{self.user.first_name}  {self.user.last_name}"


class FriendRequest(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_by')
    requested_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_to')
    STATUS_CHOICES = [
        ("Pending", 'Pending'),
        ("Accepted", 'Accepted'),
        ("Rejected", 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")
    accepted_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "friend_requests"
        ordering = ["-id"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__status = self.status

    def __str__(self):
        return f"{self.user.username} - {self.requested_to.username}: {self.status}"

    def save(self, *args, **kwargs):
        if self.status == "Accepted" and self.status != self.__status:
            self.user.friend_list.friends.add(self.requested_to)
            self.requested_to.friend_list.friends.add(self.user)
            self.accepted_date = datetime.datetime.now()
        super().save(*args, **kwargs)
