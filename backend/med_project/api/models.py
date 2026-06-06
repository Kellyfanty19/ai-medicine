from django.db import models

class MedicalUser(models.Model):
    ROLE_CHOICES = [
        ('patient', 'Пациент'),
        ('doctor', 'Врач'),
        ('admin', 'Администратор'),
    ]

    # Общие поля для всех
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    iin = models.CharField(max_length=12, unique=True, verbose_name="ИИН")
    password = models.CharField(max_length=100) # В учебном проекте можно хранить текстом
    name = models.CharField(max_length=150, verbose_name="ФИО")

    # Поля для Пациента (могут быть пустыми для доктора/админа)
    age = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.CharField(max_length=20, blank=True, null=True)
    blood_type = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    clinic = models.CharField(max_length=150, blank=True, null=True)
    district = models.CharField(max_length=50, blank=True, null=True)
    symptoms = models.TextField(blank=True, null=True)
    chronic = models.TextField(blank=True, null=True)

    # Поля для Врача
    specialization = models.CharField(max_length=150, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    experience = models.CharField(max_length=20, blank=True, null=True)
    workplace = models.CharField(max_length=150, blank=True, null=True)
    schedule = models.CharField(max_length=100, blank=True, null=True)

    # Поля для Администратора
    institution = models.CharField(max_length=150, blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    admin_name = models.CharField(max_length=150, blank=True, null=True)
    total_patients = models.CharField(max_length=20, blank=True, null=True)
    active_doctors = models.CharField(max_length=20, blank=True, null=True)
    active_districts = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.get_role_display()} - {self.name}"
