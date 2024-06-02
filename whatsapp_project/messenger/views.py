import openpyxl
from django.shortcuts import render, redirect
from .forms import ExcelUploadForm
from .models import Contact
from twilio.rest import Client

def upload_file(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return redirect('send_messages')
    else:
        form = ExcelUploadForm()
    return render(request, 'upload.html', {'form': form})

def handle_uploaded_file(f):
    workbook = openpyxl.load_workbook(f)
    sheet = workbook.active
    for row in sheet.iter_rows(min_row=2, values_only=True):
        name, message, whatsapp_number = row
        Contact.objects.create(name=name, message=message, whatsapp_number=whatsapp_number)

def send_messages(request):
    contacts = Contact.objects.all()
    if request.method == 'POST':
        send_whatsapp_messages(contacts)
        return render(request, 'success.html')
    return render(request, 'send.html', {'contacts': contacts})

def send_whatsapp_messages(contacts):
    account_sid = 'your_twilio_account_sid'
    auth_token = 'your_twilio_auth_token'
    client = Client(account_sid, auth_token)
    from_whatsapp_number = 'whatsapp:+14155238886'  # Twilio sandbox number

    for contact in contacts:
        to_whatsapp_number = f'whatsapp:{contact.whatsapp_number}'
        client.messages.create(body=contact.message,
                               from_=from_whatsapp_number,
                               to=to_whatsapp_number)