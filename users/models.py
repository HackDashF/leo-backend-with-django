from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # although we add nothing to the User class at this point,
    # we are taking control of the User class from the auth module
    # this enables us to modify the User class in the future, if needed,
    # 
    # without this placeholder, changing the User class in the future 
    # breaks the migrations system
    pass
