from django.db import models
from django.contrib.auth.models import User
from crum import get_current_user
from django.utils import timezone


class session (models.Model):
    admin = models.ForeignKey(User, on_delete=models.DO_NOTHING, default=get_current_user)

    date = models.DateField(default=timezone.localdate)
    start_time = models.TimeField(default=timezone.localtime)
    end_time = models.TimeField(blank=True, null=True, default=None)
    cash_due = models.PositiveIntegerField(blank=True, null=True, default=0)
    cash_received = models.PositiveIntegerField(blank=True, null=True, default=0)
    cash_taken = models.PositiveIntegerField(blank=True, null=True, default=0)
    keterangan = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        start_string = str(self.date) + " " + self.start_time.strftime("%I:%M %p")
        end_string = None if self.end_time is None else str(self.date) + " " + self.end_time.strftime("%I:%M %p")
        return "%s: \t%s - %s" % (self.admin.username, start_string, end_string)


class changelog (models.Model):
    type = models.CharField(max_length=64)
    pointer = models.CharField(max_length=64)
    date = models.DateField(default=timezone.localdate)
    time = models.TimeField(default=timezone.localtime)
    old = models.CharField(max_length=255, null=True)
    new = models.CharField(max_length=255, null=True)
    admin = models.ForeignKey(User, on_delete=models.DO_NOTHING, default=get_current_user)

    def __str__(self):
        return f"{self.type}/{str(self.date)}"
