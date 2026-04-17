from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Contact
from datetime import date


def dashboard(request):
    today = date.today()
    total_count = Contact.objects.count()
    today_count = Contact.objects.filter(created_at__date=today).count()
    cards = Contact.objects.order_by('-id')[:6]

    return render(request, 'Dashboard.html', {
        'total_count': total_count,
        'today_count': today_count,
        'cards': cards
    })


def list_contacts(request):
    query = request.GET.get('q')

    if query:
        contacts = Contact.objects.filter(company__icontains=query)
    else:
        contacts = Contact.objects.all()

    # 🔥 AJAX LIVE SEARCH
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string("partials/contact_table.html", {"contacts": contacts})
        return JsonResponse({"html": html})

    return render(request, "List.html", {"contacts": contacts})

def add_contact(request):
    if request.method == "POST":

        company = request.POST.get("company")
        owner = request.POST.get("owner")
        ceo = request.POST.get("ceo")
        manager = request.POST.get("manager")

        emails = request.POST.getlist("email[]")
        phones = request.POST.getlist("phone[]")

        platforms = request.POST.getlist("platform[]")
        links = request.POST.getlist("link[]")

        social_data = []
        for i in range(len(platforms)):
            if links[i]:
                social_data.append(f"{platforms[i]}:{links[i]}")

        Contact.objects.create(
            company=company,
            owner=owner,
            ceo=ceo,
            manager=manager,
            email=",".join(emails),
            phone=",".join(phones),
            social_links=",".join(social_data),
            front_image=request.FILES.get("front_image"),
            back_image=request.FILES.get("back_image"),
            qr_image=request.FILES.get("qr_image"),   # ✅ THIS WAS MISSING
            address=request.POST.get('address')
        )

        return redirect("list")

    return render(request, "Add_Addressbook.html")


def delete_contact(request, id):
    contact = get_object_or_404(Contact, id=id)
    contact.delete()
    return redirect('list')


def view_contact(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)
    return render(request, 'view.html', {'contact': contact})


def edit_contact(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)

    if request.method == "POST":
        contact.company = request.POST.get("company")
        contact.owner = request.POST.get("owner")
        contact.ceo = request.POST.get("ceo")
        contact.manager = request.POST.get("manager")

        # update images if new uploaded
        if request.FILES.get("front_image"):
            contact.front_image = request.FILES.get("front_image")

        if request.FILES.get("back_image"):
            contact.back_image = request.FILES.get("back_image")

        if request.FILES.get("qr_image"):
            contact.qr_image = request.FILES.get("qr_image")

        contact.save()
        return redirect('list')

    return render(request, "edit.html", {"contact": contact})