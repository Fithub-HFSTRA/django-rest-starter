from django.db import models

class UserPrompt(models.Model):
    user_id = models.CharField(max_length=100)
    prompt = models.TextField()
    watch_time = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_id} - {self.watch_time}"
