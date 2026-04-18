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

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string("partials/contact_table.html", {"contacts": contacts})
        return JsonResponse({"html": html})

    return render(request, "List.html", {"contacts": contacts})


# ===================== ADD =====================
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
            if i < len(links) and links[i].strip():
                social_data.append(f"{platforms[i]}:{links[i]}")

        Contact.objects.create(
            company=company,
            owner=owner,
            ceo=ceo,
            manager=manager,
            email=",".join([e for e in emails if e.strip()]),
            phone=",".join([p for p in phones if p.strip()]),
            social_links=",".join(social_data),
            front_image=request.FILES.get("front_image"),
            back_image=request.FILES.get("back_image"),
            qr_image=request.FILES.get("qr_image"),
            address=request.POST.get('address')
        )

        from django.contrib import messages

        messages.success(request, "Contact Created Successfully!")
        return redirect("list")

    return render(request, "Add_Addressbook.html")


# ===================== DELETE =====================
def delete_contact(request, id):
    contact = get_object_or_404(Contact, id=id)
    contact.delete()
    return redirect('list')


# ===================== VIEW =====================
def view_contact(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)
    return render(request, 'view.html', {'contact': contact})

# ===================== EDIT (FINAL FIXED) =====================
def edit_contact(request, contact_id):
    from django.contrib import messages

    contact = get_object_or_404(Contact, id=contact_id)

    if request.method == "POST":

        contact.company = request.POST.get("company")
        contact.owner = request.POST.get("owner")
        contact.ceo = request.POST.get("ceo")
        contact.manager = request.POST.get("manager")
        contact.address = request.POST.get("address")

        # ===== EMAIL =====
        emails = request.POST.getlist("email[]")
        contact.email = ",".join([e for e in emails if e.strip()])

        # ===== PHONE =====
        codes = request.POST.getlist("code[]")
        phones = request.POST.getlist("phone[]")

        phone_data = []
        for i in range(len(phones)):
            if phones[i].strip():
                code = codes[i] if i < len(codes) else "+91"
                phone_data.append(f"{code}-{phones[i]}")

        contact.phone = ",".join(phone_data)

        # ===== SOCIAL =====
        platforms = request.POST.getlist("platform[]")
        links = request.POST.getlist("link[]")

        social_data = []
        for i in range(len(platforms)):
            if i < len(links) and links[i].strip():
                social_data.append(f"{platforms[i]}:{links[i]}")

        contact.social_links = ",".join(social_data)

        # ===== IMAGES =====
        if request.FILES.get("front_image"):
            contact.front_image = request.FILES.get("front_image")

        if request.FILES.get("back_image"):
            contact.back_image = request.FILES.get("back_image")

        if request.FILES.get("qr_image"):
            contact.qr_image = request.FILES.get("qr_image")

        # ✅ SAVE (you missed this earlier)
        contact.save()

        # ✅ MESSAGE
        messages.success(request, "Contact updated successfully!")

        # ✅ REDIRECT BACK TO EDIT PAGE
        return redirect("edit", contact_id=contact.id)

    # ===== PRE-FILL DATA =====
    emails = contact.email.split(",") if contact.email else []
    phones = []

    if contact.phone:
        for p in contact.phone.split(","):
            if "-" in p:
                code, number = p.split("-", 1)
            else:
                code = "+91"
                number = p
            phones.append({
                "code": code,
                "number": number
            })

    socials = []
    if contact.social_links:
        for item in contact.social_links.split(","):
            parts = item.split(":", 1)
            if len(parts) == 2:
                p, l = parts
                socials.append({
                    "platform": p.strip(),
                    "link": l.strip()
                })

    return render(request, "edit.html", {
        "contact": contact,
        "emails": emails,
        "phones": phones,
        "socials": socials
    })