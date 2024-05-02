from django.db import models
from django.contrib.auth.models import User

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        if self.user:
            return f'{self.first_name} {self.last_name} ({self.user.username})'
        else:
            return f'{self.first_name} {self.last_name}'

class MethodBook(models.Model):

    university = models.CharField(max_length=255)
    institute = models.CharField(max_length=255)

    type_of_work = models.CharField(max_length=255)
    name_of_work = models.CharField(max_length=255)

    authors = models.ManyToManyField(Author, related_name='method_books')
    link = models.CharField(max_length=255)
    date_publish = models.DateField()

    agreement_author_id = models.IntegerField(null=True)
    agreement_date = models.DateField(null=True)

    def __str__(self):
        return self.name_of_work
