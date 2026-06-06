import json
from pathlib import Path

from django.http import FileResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import MedicalUser


ROLE_NAMES = {
    "patient": "Пациент",
    "doctor": "Врач",
    "admin": "Администратор",
}

DEFAULT_NAMES = {
    "patient": "Новый пациент",
    "doctor": "Новый врач",
    "admin": "Новый администратор",
}

PATIENT_PROFILE_FIELDS = {
    "name": "name",
    "birthDate": "birth_date",
    "gender": "gender",
    "bloodType": "blood_type",
    "phone": "phone",
    "clinic": "clinic",
    "district": "district",
    "symptoms": "symptoms",
    "chronic": "chronic",
}

DOCTOR_PROFILE_FIELDS = {
    "name": "name",
    "specialization": "specialization",
    "category": "category",
    "experience": "experience",
    "institution": "institution",
    "workplace": "workplace",
    "schedule": "schedule",
    "phone": "phone",
}

ADMIN_PROFILE_FIELDS = {
    "name": "name",
    "institution": "institution",
    "address": "address",
    "phone": "phone",
    "totalPatients": "total_patients",
    "activeDoctors": "active_doctors",
    "activeDistricts": "active_districts",
    "adminName": "admin_name",
}

PROFILE_FIELDS_BY_ROLE = {
    "patient": PATIENT_PROFILE_FIELDS,
    "doctor": DOCTOR_PROFILE_FIELDS,
    "admin": ADMIN_PROFILE_FIELDS,
}


def home_view(request):
    frontend_index = Path(__file__).resolve().parents[3] / "frontend" / "index-2.html"
    return FileResponse(open(frontend_index, "rb"), content_type="text/html")


def build_user_data(user):
    role_name = ROLE_NAMES.get(user.role, user.get_role_display())
    data = {
        "roleName": role_name,
        "title": f"Личный кабинет ({role_name})",
        "name": user.name,
        "iin": user.iin,
    }

    if user.role == "patient":
        data.update({
            "age": user.age,
            "gender": user.gender,
            "birthDate": user.birth_date,
            "bloodType": user.blood_type,
            "phone": user.phone,
            "clinic": user.clinic,
            "district": user.district,
            "symptoms": user.symptoms,
            "chronic": user.chronic,
        })
    elif user.role == "doctor":
        data.update({
            "specialization": user.specialization,
            "category": user.category,
            "experience": user.experience,
            "institution": user.institution,
            "workplace": user.workplace,
            "schedule": user.schedule,
            "phone": user.phone,
        })
    elif user.role == "admin":
        data.update({
            "institution": user.institution,
            "address": user.address,
            "phone": user.phone,
            "totalPatients": user.total_patients,
            "activeDoctors": user.active_doctors,
            "activeDistricts": user.active_districts,
            "adminName": user.admin_name,
        })

    return data


def validate_role_and_iin(role, iin):
    if role not in PROFILE_FIELDS_BY_ROLE:
        return "Выберите корректную роль."
    if not iin:
        return "Введите ИИН или служебный ID."
    if len(iin) != 12 or not iin.isdigit():
        return "Введите ИИН / служебный ID ровно из 12 цифр."
    return None


@csrf_exempt
def login_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        role = data.get("role", "").lower()
        iin = data.get("iin", "")
        password = data.get("password", "")

        validation_error = validate_role_and_iin(role, iin)
        if validation_error:
            return JsonResponse({"error": validation_error}, status=400)

        user = MedicalUser.objects.filter(iin=iin).first()

        if user:
            if user.password and user.password != password:
                return JsonResponse({"error": "Неверный пароль"}, status=400)
            if user.role != role:
                return JsonResponse({"error": "Этот ИИН / ID зарегистрирован с другой ролью"}, status=400)
        else:
            user = MedicalUser.objects.create(
                role=role,
                iin=iin,
                password=password,
                name=DEFAULT_NAMES.get(role, "Новый пользователь"),
            )

        return JsonResponse({"success": True, "user_data": build_user_data(user)})

    except Exception as e:
        return JsonResponse({"error": f"Ошибка сервера: {str(e)}"}, status=500)


@csrf_exempt
def save_profile_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        role = data.get("role", "").lower()
        iin = data.get("iin", "")
        profile = data.get("profile", {})

        validation_error = validate_role_and_iin(role, iin)
        if validation_error:
            return JsonResponse({"error": validation_error}, status=400)

        profile_fields = PROFILE_FIELDS_BY_ROLE[role]
        user, _ = MedicalUser.objects.get_or_create(
            iin=iin,
            defaults={
                "role": role,
                "password": "",
                "name": DEFAULT_NAMES.get(role, "Новый пользователь"),
            },
        )

        if user.role != role:
            return JsonResponse({"error": "Этот ИИН / ID зарегистрирован с другой ролью"}, status=400)

        for frontend_key, model_field in profile_fields.items():
            if frontend_key in profile:
                setattr(user, model_field, profile.get(frontend_key) or "")

        user.save()
        return JsonResponse({"success": True, "user_data": build_user_data(user)})

    except Exception as e:
        return JsonResponse({"error": f"Ошибка сервера: {str(e)}"}, status=500)
