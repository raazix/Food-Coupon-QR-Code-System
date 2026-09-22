import json
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from decouple import config
import csv
import uuid
import io
import threading
from django.core.management import call_command
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from .models import Student


@login_required(login_url='/admin/login/')
def scanner_page(request):
    return render(request, 'students/scanner.html')


@login_required(login_url='/admin/login/')
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

@login_required(login_url='/admin/login/')
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


@staff_member_required
def upload_csv(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a valid .csv file.')
            return render(request, 'students/csv_upload.html')
            
        try:
            decoded = csv_file.read().decode('utf-8-sig')
            reader = csv.DictReader(io.StringIO(decoded))
            
            created = 0
            skipped = 0
            errors = []
            
            for row in reader:
                usn = row.get('USN', '').strip().upper()
                if not usn:
                    continue
                    
                if Student.objects.filter(usn=usn).exists():
                    skipped += 1
                    continue
                    
                food = row.get('Food', '').strip()
                if food not in ['Veg', 'Non-Veg']:
                    errors.append(f"{usn}: unknown food type '{food}', set to Veg")
                    food = 'Veg'
                    
                Student.objects.create(
                    name=row.get('Name', '').strip(),
                    usn=usn,
                    section=row.get('Section', '').strip(),
                    food_type=food,
                    email=row.get('Email', '').strip().lower(),
                    qr_id=uuid.uuid4(),
                    is_used=False,
                    email_sent=False,
                )
                created += 1
                
            msg = f"Import complete — Created: {created}, Skipped (duplicates): {skipped}"
            if errors:
                msg += f" | Warnings: {'; '.join(errors)}"
            messages.success(request, msg)
            
        except Exception as e:
            messages.error(request, f"Error reading file: {str(e)}")
            return render(request, 'students/csv_upload.html')
            
        return render(request, 'students/csv_upload.html')
        
    return render(request, 'students/csv_upload.html')

def send_emails_in_background():
    try:
        call_command('send_qr_emails')
    except Exception as e:
        print(f"Background email error: {e}")

@staff_member_required
def trigger_send_emails(request):
    thread = threading.Thread(target=send_emails_in_background)
    thread.daemon = True
    thread.start()
    
    messages.success(request, "Emails are now being sent in the background. Please wait a few minutes for them to arrive.")
    return redirect('admin:students_student_changelist')