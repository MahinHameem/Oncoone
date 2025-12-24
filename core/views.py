from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import EmailMessage
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.utils import timezone
import json


from .models import Registration


@csrf_exempt
def register_view(request):
    if request.method != 'POST':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)

    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    contact = request.POST.get('contact', '').strip()
    course = request.POST.get('course', '').strip() or 'Course'
    auto_bridge = request.POST.get('autoBridge', 'false').lower() in ('1', 'true', 'yes')
    proof = request.FILES.get('proof')

    if not (name and email and contact):
        return HttpResponseBadRequest('Missing required fields')

    # read uploaded file bytes for DB storage (if provided)
    proof_bytes = None
    proof_name = None
    proof_mime = None
    # validate uploaded file (type + size) before reading into DB
    if proof:
        allowed_mimes = ('image/png', 'image/jpeg', 'image/jpg', 'application/pdf')
        max_size = 5 * 1024 * 1024  # 5 MB
        proof_name = proof.name
        proof_mime = getattr(proof, 'content_type', None)
        if proof_mime and proof_mime.lower() not in allowed_mimes:
            return HttpResponseBadRequest('Unsupported file type')
        if hasattr(proof, 'size') and proof.size and proof.size > max_size:
            return HttpResponseBadRequest('File too large (max 5MB)')
        try:
            proof_bytes = proof.read()
            # rewind uploaded file so assigning it to model.FileField still saves correctly
            try:
                proof.seek(0)
            except Exception:
                pass
        except Exception:
            proof_bytes = None

    reg = Registration.objects.create(
        name=name,
        email=email,
        contact=contact,
        course=course,
        auto_bridge=auto_bridge,
        proof=proof if proof else None,
        proof_name=proof_name,
        proof_mime=proof_mime,
        proof_data=proof_bytes,
    )

    # Send admin notification email (attach proof if present)
    admin_email = getattr(settings, 'ADMIN_EMAIL', '')
    subject = f'New registration: {reg.name} for {reg.course}'
    body = f"Name: {reg.name}\nEmail: {reg.email}\nContact: {reg.contact}\nCourse: {reg.course}\nAuto bridge: {reg.auto_bridge}\nSubmitted: {reg.created_at}\n"

    if admin_email:
        try:
            email_msg = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [admin_email])
            if reg.proof:
                # read file content and attach; derive mime safely
                reg.proof.open()
                mime = None
                if hasattr(reg.proof, 'file') and hasattr(reg.proof.file, 'content_type'):
                    mime = reg.proof.file.content_type
                elif reg.proof_mime:
                    mime = reg.proof_mime
                email_msg.attach(reg.proof.name.split('/')[-1], reg.proof.read(), mime)
                reg.proof.close()
            email_msg.send(fail_silently=False)
        except Exception as exc:  # surface email errors instead of silently swallowing
            print(f"Email send failed: {exc}")
            raise

    # Send confirmation email to the registrant (no attachment to keep it lightweight)
    if reg.email:
        try:
            user_subject = f"We received your registration for {reg.course}"
            user_body = (
                f"Hi {reg.name},\n\n"
                f"Thank you for registering for {reg.course}. We have received your details and will be in touch shortly.\n"
                f"If you have questions, reply to this email.\n\n"
                f"– OncoOne Team"
            )
            EmailMessage(user_subject, user_body, settings.DEFAULT_FROM_EMAIL, [reg.email]).send(fail_silently=True)
        except Exception:
            # don't block flow if user confirmation fails
            pass

    return JsonResponse({'status': 'ok', 'id': reg.id})


# Admin API: list, edit, delete registrations (development use only)
@csrf_exempt
def registrations_list(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    regs = Registration.objects.order_by('-created_at').all()
    data = []
    for r in regs:
        proof_url = None
        if r.proof:
            try:
                proof_url = request.build_absolute_uri(r.proof.url)
            except Exception:
                proof_url = None
        has_db_proof = bool(r.proof_data)
        download_url = request.build_absolute_uri(f'/api/admin/registrations/{r.id}/download/')
        data.append({
            'id': r.id,
            'name': r.name,
            'email': r.email,
            'contact': r.contact,
            'course': r.course,
            'auto_bridge': r.auto_bridge,
            'created_at': r.created_at.isoformat(),
            'has_db_proof': has_db_proof,
            'download_url': download_url,
        })
    return JsonResponse({'results': data})


@csrf_exempt
def registration_detail(request, pk):
    reg = get_object_or_404(Registration, pk=pk)

    if request.method == 'GET':
        has_db_proof = bool(reg.proof_data)
        download_url = request.build_absolute_uri(f'/api/admin/registrations/{reg.id}/download/')
        return JsonResponse({
            'id': reg.id,
            'name': reg.name,
            'email': reg.email,
            'contact': reg.contact,
            'course': reg.course,
            'auto_bridge': reg.auto_bridge,
            'created_at': reg.created_at.isoformat(),
            'has_db_proof': has_db_proof,
            'download_url': download_url,
        })

    if request.method in ('PUT', 'PATCH'):
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except Exception:
            return HttpResponseBadRequest('Invalid JSON')

        changed = False
        for field in ('name', 'email', 'contact', 'course'):
            if field in payload:
                setattr(reg, field, payload[field])
                changed = True
        if 'auto_bridge' in payload:
            reg.auto_bridge = bool(payload['auto_bridge'])
            changed = True
        if changed:
            reg.save()
        return JsonResponse({'status': 'ok'})

    if request.method == 'DELETE':
        # delete attached file from storage
        if reg.proof:
            try:
                reg.proof.delete(save=False)
            except Exception:
                pass
        reg.delete()
        return JsonResponse({'status': 'deleted'})

    return HttpResponseNotAllowed(['GET', 'PUT', 'PATCH', 'DELETE'])


@staff_member_required
def download_proof_db(request, pk):
    reg = get_object_or_404(Registration, pk=pk)
    if not reg.proof_data:
        return HttpResponse(status=404)
    # stream DB bytes as attachment
    resp = HttpResponse(reg.proof_data, content_type=reg.proof_mime or 'application/octet-stream')
    filename = reg.proof_name or f'registration-{reg.id}-proof'
    resp['Content-Disposition'] = f'attachment; filename="{filename}"'
    return resp


@staff_member_required
def download_proof(request, pk):
    """Serve attached proof whether stored in DB (`proof_data`) or on disk (`proof`)."""
    reg = get_object_or_404(Registration, pk=pk)
    # Prefer DB-stored bytes
    if reg.proof_data:
        resp = HttpResponse(reg.proof_data, content_type=reg.proof_mime or 'application/octet-stream')
        filename = reg.proof_name or f'registration-{reg.id}-proof'
        resp['Content-Disposition'] = f'attachment; filename="{filename}"'
        return resp

    # Fallback to FileField on-disk file
    if reg.proof:
        try:
            # use FileResponse for efficient file streaming
            from django.http import FileResponse
            reg.proof.open('rb')
            filename = reg.proof.name.split('/')[-1]
            response = FileResponse(reg.proof, as_attachment=True, filename=filename)
            return response
        except Exception:
            return HttpResponse(status=500)

    return HttpResponse(status=404)


@staff_member_required
def admin_students_page(request):
    """Render the admin students page (served from Django so admin session authenticates downloads)."""
    return render(request, 'admin/students.html')


@staff_member_required
def admin_courses_page(request):
    """Render the admin courses editor page."""
    return render(request, 'admin/courses-admin.html')


def staff_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin-students-page')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            auth_login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next') or None
            return redirect(next_url or 'admin-students-page')
        error = 'Invalid credentials or not authorized.'

    return render(request, 'admin/login.html', {'error': error})


def staff_logout(request):
    if request.user.is_authenticated:
        auth_logout(request)
    return redirect('staff-login')
