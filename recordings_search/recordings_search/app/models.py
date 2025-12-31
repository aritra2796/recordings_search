from django.db import models

class AppLog(models.Model):
    LEVEL_CHOICES = (
        ("INFO", "INFO"),
        ("WARNING", "WARNING"),
        ("ERROR", "ERROR"),
    )

    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    message = models.TextField()
    user = models.CharField(max_length=150, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.level} | {self.created_at}"
