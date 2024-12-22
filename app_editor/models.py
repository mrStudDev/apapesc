from django.db import models

class NotasApapescModel(models.Model):
    titulo = models.CharField(max_length=100, blank=True, null=True)
    content = models.TextField()

    def __str__(self):
        return self.titulo if self.titulo else "Nota sem título"
