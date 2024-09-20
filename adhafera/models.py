from django.conf import settings
from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models


class List(models.Model):
    # should be created along with a ListUser (the creator)
    # should be deleted if, ever, there are no ListUser records for this list

    LIST_TYPE_BASIC = 'BASIC'
    LIST_TYPE_QUANT = 'QUANT'

    LIST_TYPE_CHOICES = [
        (LIST_TYPE_BASIC, "Basic"),
        (LIST_TYPE_QUANT, "Quantities"),
    ]

    title = models.CharField(max_length=100)
    list_type = models.CharField(max_length=5, choices=LIST_TYPE_CHOICES, default=LIST_TYPE_BASIC)
    created_at = models.DateField(auto_now_add=True, null=True)


class Item(models.Model):
    list = models.ForeignKey(List, null=False, on_delete=models.CASCADE, related_name='items')

    quantity = models.IntegerField(null=True, validators=[MinValueValidator(1)])
    text = models.CharField(max_length=500)
    sequence_position = models.IntegerField(validators=[MinValueValidator(1)])
    checked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('list', 'sequence_position',)


class ListUser(models.Model):
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name='listusers')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    list_position = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
            unique_together = ('list', 'user',)


class ListShareCode(models.Model):
    # create - /share [POST] {username} | list_id from URL, code generated
    # apply  - /join  [POST] {code}     | username from request.user
    list = models.ForeignKey(List, on_delete=models.CASCADE)

    username = models.CharField(max_length=100)
    code = models.CharField(max_length=6, validators=[MinLengthValidator(6)])

    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        unique_together = ('list', 'username',)
