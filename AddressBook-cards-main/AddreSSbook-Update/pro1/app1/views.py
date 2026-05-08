from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Contact
from datetime import date
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User


# ===================== COMMON =====================
def get_admin_data(request):
    return {
        'is_admin': request.user.is_staff
    }


# ===================== REGISTER =====================
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm')

        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "User already exists")
            return redirect('register')

        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Registered successfully!")
        return redirect('login')

    return render(request, 'register.html')


# ===================== LOGIN =====================
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )

        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid credentials")

    return render(request, 'login.html')


# ===================== LOGOUT =====================
def logout_view(request):
    logout(request)
    return redirect('login')


# ===================== DASHBOARD =====================
@login_required
def dashboard(request):
    today = date.today()

    context = {
        'total_count': Contact.objects.count(),
        'today_count': Contact.objects.filter(created_at__date=today).count(),
        'cards': Contact.objects.order_by('-id')[:6],
    }

    context.update(get_admin_data(request))
    return render(request, 'dashboard.html', context)


# ===================== ADMIN LIST =====================
@login_required
def admin_list(request):
    if not request.user.is_staff:
        return redirect('dashboard')

    admins = User.objects.filter(is_staff=True)

    return render(request, 'add_admin.html', {
        'admins': admins
    })


# ===================== EDIT ADMIN =====================
@login_required
def edit_admin(request, id):
    if not request.user.is_superuser:
        messages.error(request, "Only superuser allowed")
        return redirect('admin_list')

    admin = get_object_or_404(User, id=id)

    if request.method == "POST":
        admin.username = request.POST.get("username")
        admin.email = request.POST.get("email")

        password = request.POST.get("password")
        if password:
            admin.set_password(password)

        admin.save()
        messages.success(request, "Updated successfully")
        return redirect('admin_list')

    return render(request, 'edit_admin.html', {'admin_user': admin})


# ===================== DELETE ADMIN =====================
@login_required
def delete_admin(request, id):
    if not request.user.is_superuser:
        messages.error(request, "Only superuser allowed")
        return redirect('admin_list')

    admin = get_object_or_404(User, id=id)

    if admin.is_superuser:
        messages.error(request, "Cannot delete superuser")
        return redirect('admin_list')

    admin.delete()
    messages.success(request, "Deleted successfully")
    return redirect('admin_list')

# ===================== CONTACT LIST =====================
@login_required
def contact_list(request):
    contacts = Contact.objects.all()

    # 🔥 search support (for your list.html)
    query = request.GET.get('q')
    if query:
        contacts = contacts.filter(company__icontains=query)

    # 🔥 AJAX support (for live search)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('partials/contact_table.html', {'contacts': contacts})
        return JsonResponse({'html': html})

    return render(request, 'list.html', {'contacts': contacts})


# ===================== ADD CONTACT =====================
@login_required
def add_contact(request):
    if request.method == "POST":
        Contact.objects.create(
            company=request.POST.get('company'),
            owner=request.POST.get('owner'),
            ceo=request.POST.get('ceo'),
            manager=request.POST.get('manager'),
            email=",".join(request.POST.getlist('email[]')),
            phone=",".join(request.POST.getlist('phone[]')),
            social_links=",".join(request.POST.getlist('link[]')),
            front_image=request.FILES.get('front_image'),
            back_image=request.FILES.get('back_image'),
            qr_image=request.FILES.get('qr_image'),
            address=request.POST.get('address')
        )

        return render(request, 'Add_Addressbook.html', {'success': True})

    return render(request, 'Add_Addressbook.html')


# ===================== VIEW CONTACT =====================
@login_required
def view_contact(request, id):
    contact = get_object_or_404(Contact, id=id)
    return render(request, 'view.html', {'contact': contact})


# ===================== EDIT CONTACT =====================
@login_required
def edit_contact(request, id):
    contact = get_object_or_404(Contact, id=id)

    if request.method == "POST":
        contact.company = request.POST.get('company')
        contact.owner = request.POST.get('owner')
        contact.ceo = request.POST.get('ceo')
        contact.manager = request.POST.get('manager')
        contact.email = ",".join(request.POST.getlist('email[]'))
        contact.phone = ",".join(request.POST.getlist('phone[]'))
        contact.social_links = ",".join(request.POST.getlist('link[]'))
        contact.address = request.POST.get('address')

        if request.FILES.get('front_image'):
            contact.front_image = request.FILES.get('front_image')

        if request.FILES.get('back_image'):
            contact.back_image = request.FILES.get('back_image')

        if request.FILES.get('qr_image'):
            contact.qr_image = request.FILES.get('qr_image')

        contact.save()

        return redirect('dashboard')

    return render(request, 'edit.html', {
        'contact': contact,
        'emails': contact.email.split(',') if contact.email else [],
        'phones': [{'number': p, 'code': '+91'} for p in contact.phone.split(',')] if contact.phone else [],
        'socials': [{'platform': 'Website', 'link': s} for s in contact.social_links.split(',')] if contact.social_links else []
    })


# ===================== DELETE CONTACT =====================
@login_required
def delete_contact(request, id):
    contact = get_object_or_404(Contact, id=id)
    contact.delete()
    return redirect('list')

@login_required
def edit_contact(request, id):
    contact = get_object_or_404(Contact, id=id)

    success = False

    if request.method == "POST":
        contact.company = request.POST.get('company')
        contact.owner = request.POST.get('owner')
        contact.ceo = request.POST.get('ceo')
        contact.manager = request.POST.get('manager')
        contact.email = ",".join(request.POST.getlist('email[]'))
        contact.phone = ",".join(request.POST.getlist('phone[]'))
        contact.social_links = ",".join(request.POST.getlist('link[]'))
        contact.address = request.POST.get('address')

        if request.FILES.get('front_image'):
            contact.front_image = request.FILES.get('front_image')

        if request.FILES.get('back_image'):
            contact.back_image = request.FILES.get('back_image')

        if request.FILES.get('qr_image'):
            contact.qr_image = request.FILES.get('qr_image')

        contact.save()

        success = True   # 👈 IMPORTANT

    return render(request, 'edit.html', {
        'contact': contact,
        'emails': contact.email.split(',') if contact.email else [],
        'phones': [{'number': p, 'code': '+91'} for p in contact.phone.split(',')] if contact.phone else [],
        'socials': [{'platform': 'Website', 'link': s} for s in contact.social_links.split(',')] if contact.social_links else [],
        'success': success   # 👈 PASS TO HTML
    })