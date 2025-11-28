from django.db import models

from account.models import CustomUser


class Group(models.Model):
    DAYS = (
        ('mon/wed/fri','пн/ср/пт'),
        ('tue/thu/sat','вт/чт/сб'),
        ('sat/sun','сб/вс')
    )
    title = models.CharField(max_length=100)
    users = models.ManyToManyField(CustomUser, related_name='custom_groups', blank=True)
    time = models.TimeField(blank=True, null=True)
    days = models.CharField(max_length=50, choices=DAYS, null=True)
    age = models.CharField(max_length=100, default='Все')
    amount = models.PositiveIntegerField(null=True, blank=True)
    image = models.ImageField(upload_to='group_images/', null=True, blank=True)
    
    def __str__(self):
        return f'{self.title} {self.time}'

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def get_users_count(self):
        return self.users.count()
    
    #сколько еще свободных мест
    def free_slots(self):
        if self.amount is None:
            return None
        return self.amount - self.get_users_count()
    
    #
    def can_add_user(self):
        return self.free_slots() is None or self.free_slots()>0
    
    #
    def as_text(self):
        return f"{self.title} | {self.get_days_display()} | {'self.time'}"