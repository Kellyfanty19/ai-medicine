import json
from pathlib import Path

from django.http import FileResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import MedicalUser


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


def home_view(request):
    frontend_index = Path(__file__).resolve().parents[3] / "frontend" / "index-2.html"
    return FileResponse(open(frontend_index, "rb"), content_type="text/html")


def build_user_data(user):
    data = {
        "roleName": user.get_role_display(),
        "title": f"Личный кабинет ({user.get_role_display()})",
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
            "experience": user.experience,
            "workplace": user.workplace,
            "schedule": user.schedule,
        })
    elif user.role == "admin":
        data.update({
            "institution": user.institution,
            "address": user.address,
            "stats": {
                "totalPatients": "В базе данных SQLite",
                "activeDoctors": "Синхронизировано",
                "activeDistricts": "10",
                "aiConsultationsToday": "1",
            },
        })

    return data


@csrf_exempt
def login_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        role = data.get("role", "").lower()
        iin = data.get("iin", "")
        password = data.get("password", "")

        if not role or not iin:
            return JsonResponse({"error": "Заполните роль и ИИН"}, status=400)
        if len(iin) != 12 or not iin.isdigit():
            return JsonResponse({"error": "Введите ИИН ровно из 12 цифр"}, status=400)

        user = MedicalUser.objects.filter(iin=iin).first()

        if user:
            if user.password and user.password != password:
                return JsonResponse({"error": "Неверный пароль"}, status=400)
            if user.role != role:
                return JsonResponse({"error": "Этот ИИН зарегистрирован с другой ролью"}, status=400)
        else:
            user = MedicalUser.objects.create(
                role=role,
                iin=iin,
                password=password,
                name="Новый пациент" if role == "patient" else "Новый пользователь",
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

        if role != "patient":
            return JsonResponse({"error": "Сохранение настроено для профиля пациента"}, status=400)
        if len(iin) != 12 or not iin.isdigit():
            return JsonResponse({"error": "Введите ИИН ровно из 12 цифр"}, status=400)

        user, _ = MedicalUser.objects.get_or_create(
            iin=iin,
            defaults={"role": "patient", "password": "", "name": "Новый пациент"},
        )

        if user.role != role:
            return JsonResponse({"error": "Этот ИИН зарегистрирован с другой ролью"}, status=400)

        for frontend_key, model_field in PATIENT_PROFILE_FIELDS.items():
            if frontend_key in profile:
                setattr(user, model_field, profile.get(frontend_key) or "")

        user.save()
        return JsonResponse({"success": True, "user_data": build_user_data(user)})

    except Exception as e:
        return JsonResponse({"error": f"Ошибка сервера: {str(e)}"}, status=500)
