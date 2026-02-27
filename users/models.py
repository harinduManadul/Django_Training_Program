from django.db import models

class User(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]
    
    name: models.CharField = models.CharField(max_length=100)
    username: models.CharField = models.CharField(max_length=100, unique=True)
    email: models.CharField = models.EmailField()
    password: models.CharField = models.CharField(max_length=100)
    role: models.CharField = models.CharField(max_length=50, choices=ROLE_CHOICES, default='user')
    device_ids: models.ManyToManyField = models.ManyToManyField('devices.Device', blank=True, related_name='users')
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    @property
    def is_admin(self):
        return self.role == 'admin'