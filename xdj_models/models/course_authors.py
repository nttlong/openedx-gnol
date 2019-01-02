from django.contrib.auth.models import User
from django.db import models
class course_authors(models.Model):
    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    # department = models.CharField(max_length=100)
    user_id =  models.IntegerField()
    course_id = models.CharField(max_length=255)
    created_on =models.DateField()
    id=models.IntegerField()
    class Meta:
        db_table = "course_authors"