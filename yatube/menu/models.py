from django.db import models


class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=200)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def __str__(self):
        return self.name
