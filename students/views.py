import json
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Student


def scanner_page(request):
    return render(request, 'students/scanner.html')


@csrf_exempt
@require_http_methods(["POST"])
@transaction.atomic
def verify_qr(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Bad request'}, status=400)

    qr_id = data.get('qr_id', '').strip()
    usn   = data.get('usn', '').strip().upper()

    if not qr_id and not usn:
        return JsonResponse({'status': 'error', 'message': 'Send qr_id or usn'}, status=400)

    # Look up by whichever field was provided
    try:
        if qr_id:
            student = Student.objects.select_for_update().get(qr_id=qr_id)
        else:
            student = Student.objects.select_for_update().get(usn=usn)
    except Student.DoesNotExist:
        return JsonResponse({'status': 'invalid', 'message': 'Not found in system'}, status=404)
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Invalid input'}, status=400)

    if student.is_used:
        return JsonResponse({
            'status': 'rejected',
            'message': 'Already used!',
            'name': student.name,
            'usn': student.usn,
        })

    student.is_used = True
    student.save(update_fields=['is_used'])

    return JsonResponse({
        'status': 'allowed',
        'name': student.name,
        'usn': student.usn,
        'section': student.section,
        'food': student.food_type,
    })


def stats_view(request):
    total  = Student.objects.count()
    used   = Student.objects.filter(is_used=True).count()
    veg    = Student.objects.filter(food_type='Veg', is_used=True).count()
    nonveg = Student.objects.filter(food_type='Non-Veg', is_used=True).count()
    return JsonResponse({
        'total': total,
        'scanned': used,
        'remaining': total - used,
        'veg_served': veg,
        'nonveg_served': nonveg,
    })