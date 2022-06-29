from django.db import models


class GenderChoices(models.TextChoices):
    Female = 'Female'
    Male = 'Male'
    Other = 'Other'
