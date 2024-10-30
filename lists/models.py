from django.db import models
from django.contrib.auth.models import User


class List(models.Model):
    name = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.TextField()
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    color = models.CharField(default='#000000', max_length=7)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
