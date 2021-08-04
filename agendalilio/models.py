from django.db import models
from django.contrib.auth.models import User

class Professional_Profile(models.Model):
    name            =   models.CharField(max_length=20, blank=True)
    address         =   models.CharField(max_length=20, blank=True)
    bio             =   models.TextField(max_length=500, blank=True)
    location        =   models.CharField(max_length=30, blank=True)
    phone           =   models.CharField(max_length=10, blank=True)
    whatsapp        =   models.CharField(max_length=11, blank=True)


class Event(models.Model):
    name            = models.CharField(max_length=255, blank=False)
    patients_name   = models.CharField(max_length=255, blank=False)
    description     = models.TextField()
    email           = models.EmailField(blank=False)
    whatsapp        = models.CharField(max_length=11, blank=False)
    phone           = models.CharField(max_length=10, blank=False)
    birth_date      = models.DateField(blank=False)
    start_datetime  = models.DateTimeField(blank=False)
    finish_datetime = models.DateTimeField(blank=False)
    location        = models.CharField(max_length=255)
    google_event_id = models.CharField(max_length=255)
    user            = models.ForeignKey(User, on_delete=models.CASCADE)

    # # Método obrigatório para o Django admin, quando chamar a classe Event, ele retorno o id
    def __str__(self):
        return str(self.id)

    # #Nome que vai no DB
    class Meta:
        db_table = 'event'


class token_google_user(models.Model):

    token = models.CharField(max_length=255, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # # Método obrigatório para o Django admin, quando chamar a classe Event, ele retorno o id
    def __str__(self):
        return str(self.id)

    # #Nome que vai no DB
    class Meta:
        db_table = 'token_google_user'


