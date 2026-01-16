from django.shortcuts import render, redirect, get_object_or_404
from .models import Case, Message, UserProfile
from .forms import CaseForm, MessageForm, EvidenceForm, UserProfileForm
import requests
from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Case as DbCase, When, Value, IntegerField
from django.http import JsonResponse
from django.conf import settings
import json
import google.generativeai as genai
import os
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
import random

# Configure Gemini
genai.configure(api_key=settings.GOOGLE_API_KEY)

def home(request):
    return render(request, 'dashboard/home.html')

@login_required
def user_dashboard(request):
    if request.user.is_superuser:
        return redirect('investigator_dashboard')
    user_cases = Case.objects.filter(user=request.user).order_by('-date_filed')
    
    active_cases = user_cases.exclude(status__in=['Resolved', 'Closed'])
    resolved_cases = user_cases.filter(status__in=['Resolved', 'Closed'])
    
    # Get unread messages (where receiver is user and sender is NOT user)
    unread_messages = Message.objects.filter(
        case__user=request.user,
        is_read=False
    ).exclude(sender=request.user).order_by('-timestamp')
    
    unread_messages_count = unread_messages.count()
    
    # Completed Cases Count (Resolved or Closed)
    completed_cases_count = resolved_cases.count()

    # Dynamic Safety Tips
    safety_tips = [
        "Never share your OTP with anyone.",
        "Enable Two-Factor Authentication (2FA) on all accounts.",
        "Use strong, unique passwords for every site.",
        "Be cautious of unsolicited emails or messages asking for personal info.",
        "Keep your software and operating system updated.",
        "Avoid clicking on suspicious links in SMS or emails.",
        "Check for HTTPS in the URL before entering sensitive data.",
        "Monitor your bank statements regularly for unauthorized transactions.",
        "Do not download attachments from unknown senders.",
        "Log out of your accounts when using public computers."
    ]
    safety_tip = random.choice(safety_tips)

    # Check for missing address
    missing_address = False
    try:
        profile = request.user.profile
        if not profile.address:
            missing_address = True
    except UserProfile.DoesNotExist:
        missing_address = True

    context = {
        'active_cases': active_cases,
        'resolved_cases': resolved_cases,
        'unread_messages_count': unread_messages_count,
        'completed_cases_count': completed_cases_count,
        'unread_messages': unread_messages,
        'safety_tip': safety_tip,
        'missing_address': missing_address
    }
    return render(request, 'dashboard/user_dashboard.html', context)

@login_required
def edit_profile(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=request.user)
        profile.save()

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            
            # Re-geocode if address changed (or if lat/lon missing)
            if 'address' in form.changed_data or 'city' in form.changed_data or 'state' in form.changed_data or 'pincode' in form.changed_data or not profile.latitude:
                lat, lon = geocode_address(
                    profile.address, 
                    profile.city, 
                    profile.state, 
                    profile.pincode
                )
                if lat and lon:
                    profile.latitude = lat
                    profile.longitude = lon
            
            profile.save()
            return redirect('user_dashboard')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'dashboard/edit_profile.html', {'form': form})

def geocode_address(address, city, state, pincode):
    # Hybrid Strategy with Split Address Logic:
    # 1. Structured Query (Best for exact matches if City is correct)
    # 2. Free Text Query (Best for handling suburbs/localities entered as City)
    # 3. Split Address: If address has commas, try the last part (locality) + City/State
    # 4. Fallback to Area/City level
    
    queries = [
        # 1. Strict Structured
        {'street': address, 'city': city, 'state': state, 'postalcode': pincode},
        
        # 2. Free Text (No Pincode)
        {'q': f"{address}, {city}, {state}"},
        
        # 3. Free Text Full
        {'q': f"{address}, {city}, {state}, {pincode}"},
    ]

    # 4. Knowledge Patch: Specific Fixes for Unmapped Societies
    # Fix 1: "Chintamani Nagar, Bibwewadi" -> VIT Pune (Landmark)
    if "chintamani nagar" in address.lower() and ("bibwewadi" in address.lower() or "bibwewadi" in city.lower()):
        queries.insert(0, {'q': "Vishwakarma Institute of Technology, Pune"})
    
    # Fix 2: "Upper Indira Nagar, Bibwewadi" -> Indira Nagar, Pune (Landmark)
    # OSM fails on "Upper Indira Nagar" but finds "Indira Nagar, Pune" correctly (18.468 vs 18.450)
    if "indira nagar" in address.lower() and ("bibwewadi" in address.lower() or "bibwewadi" in city.lower()):
        queries.insert(0, {'q': "Indira Nagar, Pune"})

    # 5. Split Address Strategy (Handle "Locality" in Address field)
    parts = [p.strip() for p in address.split(',')]
    if len(parts) > 1:
        last_part = parts[-1]
        if last_part:
            # Try Last Part + City + State (No Zip)
            queries.append({'q': f"{last_part}, {city}, {state}"})
            # Try Last Part + State (No City/Zip)
            queries.append({'q': f"{last_part}, {state}"})
            # Try Last Part + City + State + Zip
            queries.append({'q': f"{last_part}, {city}, {state}, {pincode}"})

    # 6. Smart Cleaning Strategy (Handle "Phase 2", "Part 1", etc.)
    first_part = parts[0]
    import re
    cleaned_part = re.sub(r'\s+(phase|part|sector)\s*\d+', '', first_part, flags=re.IGNORECASE).strip()
    
    if cleaned_part and cleaned_part != first_part:
        # If cleaning changed something, try the cleaned version
        # Try Cleaned Part + City + State
        queries.append({'q': f"{cleaned_part}, {city}, {state}"})

    # 7. Fallbacks
    queries.extend([
        {'q': f"{city}, {state}"}, # City level (No Zip)
        {'q': f"{city}, {state}, {pincode}"}
    ])
    
    url = "https://nominatim.openstreetmap.org/search"
    headers = {
        'User-Agent': 'CyberCrimeDashboard/1.0'
    }

    for params in queries:
        params['format'] = 'json'
        params['limit'] = 1
        
        try:
            response = requests.get(url, params=params, headers=headers)
            if response.status_code == 200 and response.json():
                data = response.json()[0]
                return float(data['lat']), float(data['lon'])
        except Exception as e:
            print(f"Geocoding error for {params}: {e}")
            
    return None, None

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if form.is_valid() and profile_form.is_valid():
            user = form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            
            # Geocode
            lat, lon = geocode_address(
                profile.address, 
                profile.city, 
                profile.state, 
                profile.pincode
            )
            if lat and lon:
                profile.latitude = lat
                profile.longitude = lon
            
            profile.save()
            
            login(request, user)
            return redirect('user_dashboard')
    else:
        form = UserCreationForm()
        profile_form = UserProfileForm()
    return render(request, 'registration/signup.html', {'form': form, 'profile_form': profile_form})

@login_required
def get_heatmap_data(request):
    # Only return data for users who have filed at least one case
    # We want to show higher intensity where more complaints originate.
    # We can return a list of points, one for each case filed.
    
    cases = Case.objects.select_related('user__profile').filter(
        user__profile__latitude__isnull=False,
        user__profile__longitude__isnull=False
    )
    
    heatmap_data = []
    for case in cases:
        heatmap_data.append([
            case.user.profile.latitude,
            case.user.profile.longitude,
            1 # Intensity weight (can be adjusted)
        ])
        
    return JsonResponse({'data': heatmap_data})

@login_required
def investigator_dashboard(request):
    if not request.user.is_superuser:
        return redirect('user_dashboard')

    if request.method == 'POST' and 'mark_read' in request.POST:
        message_id = request.POST.get('message_id')
        if message_id:
            try:
                msg = Message.objects.get(id=message_id)
                msg.is_read = True
                msg.save()
            except Message.DoesNotExist:
                pass
        return redirect('investigator_dashboard')

        return redirect('investigator_dashboard')

    # Define status priority
    status_priority = DbCase(
        When(status='Submitted', then=Value(1)),
        When(status='Under Review', then=Value(2)),
        When(status='In Progress', then=Value(3)),
        When(status='Resolved', then=Value(4)),
        When(status='Closed', then=Value(5)),
        default=Value(6),
        output_field=IntegerField(),
    )

    all_cases = Case.objects.annotate(priority=status_priority).order_by('priority', '-date_filed')
    
    # Calculate stats
    total_cases = all_cases.count()
    pending_cases = all_cases.filter(status='Submitted').count()
    # Resolved includes 'Resolved' and 'Closed'
    resolved_cases = all_cases.filter(status__in=['Resolved', 'Closed']).count()
    # Active includes 'In Progress' and 'Under Review'
    active_cases = all_cases.filter(status__in=['In Progress', 'Under Review']).count()
    
    success_rate = 0
    if total_cases > 0:
        success_rate = int((resolved_cases / total_cases) * 100)

    # Chart Data
    case_type_data = Case.objects.values('case_type').annotate(count=Count('case_type'))
    chart_labels = [item['case_type'] for item in case_type_data]
    chart_data = [item['count'] for item in case_type_data]

    # AI Insights Generation
    ai_insights = "No insights available."
    try:
        # Aggregate stats for the prompt
        case_types = list(all_cases.values_list('case_type', flat=True))
        type_counts = {ctype: case_types.count(ctype) for ctype in set(case_types)}
        
        prompt = (
            f"Analyze the following cybercrime statistics and provide exactly 3 actionable insights. "
            f"Format as simple bullet points. "
            f"Each point must be a single, direct sentence without bold headers or labels. "
            f"Focus on the key takeaway and keep it concise.\n\n"
            f"Statistics:\n"
            f"Total Cases: {total_cases}\n"
            f"Pending: {pending_cases}\n"
            f"Resolved: {resolved_cases}\n"
            f"Case Types Breakdown: {type_counts}"
        )
        
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        response = model.generate_content(prompt)
        ai_insights = response.text.strip()
    except Exception as e:
        ai_insights = f"Could not generate insights: {str(e)}"

    # Recent Victim Messages
    # Filter messages where sender is the case owner (victim) AND is_read is False
    recent_messages = Message.objects.filter(sender=F('case__user'), is_read=False).order_by('-timestamp')

    # Limit cases for the main dashboard view
    recent_cases = all_cases[:5]

    context = {
        'cases': recent_cases,
        'total_cases': total_cases,
        'active_cases': active_cases,
        'pending_cases': pending_cases,
        'resolved_cases': resolved_cases,
        'success_rate': success_rate,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'ai_insights': ai_insights,
        'recent_messages': recent_messages
    }
    return render(request, 'dashboard/investigator_dashboard.html', context)

@login_required
def all_complaints(request):
    if not request.user.is_superuser:
        return redirect('user_dashboard')
    
    status_filter = request.GET.get('status')
    
    # Define status priority
    status_priority = DbCase(
        When(status='Submitted', then=Value(1)),
        When(status='Under Review', then=Value(2)),
        When(status='In Progress', then=Value(3)),
        When(status='Resolved', then=Value(4)),
        When(status='Closed', then=Value(5)),
        default=Value(6),
        output_field=IntegerField(),
    )

    all_cases = Case.objects.annotate(priority=status_priority).order_by('priority', '-date_filed')
    
    if status_filter:
        all_cases = all_cases.filter(status=status_filter)
    
    context = {
        'cases': all_cases,
        'status_choices': Case.STATUS_CHOICES,
        'current_status': status_filter
    }
    return render(request, 'dashboard/all_complaints.html', context)

@login_required
def file_report(request):
    if request.method == 'POST':
        form = CaseForm(request.POST)
        if form.is_valid():
            case = form.save(commit=False)
            case.user = request.user
            case.save()
            return redirect('user_dashboard')
    else:
        form = CaseForm()
    
    context = {'form': form}
    return render(request, 'dashboard/file_report.html', context)

@login_required
def case_detail(request, case_id):
    case = get_object_or_404(Case, id=case_id)
    if not request.user.is_superuser and case.user != request.user:
        return redirect('user_dashboard')

    # Mark unread messages as read when viewing the case
    # Only mark messages sent by others (e.g. investigator) as read
    unread_messages = case.messages.filter(is_read=False).exclude(sender=request.user)
    unread_messages.update(is_read=True)

    if request.method == 'POST':
        if 'send_message' in request.POST:
            message_form = MessageForm(request.POST)
            if message_form.is_valid():
                message = message_form.save(commit=False)
                message.case = case
                message.sender = request.user
                message.save()
                return redirect('case_detail', case_id=case.id)
        
        elif 'upload_evidence' in request.POST:
            evidence_form = EvidenceForm(request.POST, request.FILES)
            if evidence_form.is_valid():
                evidence = evidence_form.save(commit=False)
                evidence.case = case
                evidence.save()
                return redirect('case_detail', case_id=case.id)

    else:
        message_form = MessageForm()
        evidence_form = EvidenceForm()

    context = { 
        'case': case, 
        'messages': case.messages.all().order_by('timestamp'), 
        'evidence_list': case.evidence.all().order_by('-uploaded_at'),
        'form': message_form, 
        'evidence_form': evidence_form 
    }
    return render(request, 'dashboard/case_detail.html', context)

@login_required
def update_case_status(request, case_id):
    if not request.user.is_superuser:
        return redirect('home')

    case = get_object_or_404(Case, id=case_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            case.status = new_status
            case.save()
        return redirect('investigator_dashboard')
    
    context = {'case': case, 'status_choices': Case.STATUS_CHOICES}
    return render(request, 'dashboard/update_case.html', context)

def chatbot_response(request):
    if request.method == 'POST':
        try:
            system_prompt = (
                "You are 'CyberShield AI', a compassionate and helpful AI assistant for a cybercrime reporting platform. "
                "Your only purpose is to support victims of cybercrime. "
                "Your tone must be calm, empathetic, and professional. "
                "You must strictly follow these rules:\n"
                "1. **Stay On Topic:** Only discuss topics directly related to cybercrime, online safety, and the reporting process.\n"
                "2. **Encourage, Don't Force:** If a user is scared or hesitant, be reassuring.\n"
                "3. **Provide General Knowledge:** You can explain what phishing, ransomware, etc., are.\n"
                "4. **Guide, Don't Advise:** Do not give legal or financial advice.\n"
                "5. **Do Not Ask for Personal Info:** Never ask for passwords, credit card numbers, or other sensitive personal data.\n"
                "6. **Use Formatting:** Use Markdown for formatting."
            )

            data = json.loads(request.body)
            user_message = data.get('message', '')
            language = data.get('language', 'English')

            model = genai.GenerativeModel('models/gemini-2.5-flash')
            response = model.generate_content(f"{system_prompt}\n\nIMPORTANT: You must respond in {language}.\n\nUSER'S MESSAGE: '{user_message}'")
            bot_response = response.text

            return JsonResponse({'response': bot_response})
        
        except Exception as e:
            return JsonResponse({'response': f"Sorry, I'm having trouble connecting to my brain right now. Error: {e}"})

    return JsonResponse({'error': 'Invalid request'}, status=400)

def predict_case_type(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            description = data.get('description', '')
            
            if not description:
                return JsonResponse({'error': 'No description provided'}, status=400)

            prompt = (
                f"Analyze the following cybercrime incident description and suggest the most likely Case Type and Department. "
                f"Case Types: {[t[0] for t in Case.CASE_TYPES]}. "
                f"Departments: {[d[0] for d in Case.DEPARTMENT_CHOICES]}. "
                f"Return the response in this format: 'Case Type | Department'. "
                f"\n\nDescription: {description}"
            )

            model = genai.GenerativeModel('models/gemini-2.5-flash')
            response = model.generate_content(prompt)
            result = response.text.strip()
            
            suggested_type = ""
            suggested_department = ""

            if "|" in result:
                parts = result.split("|")
                suggested_type = parts[0].strip()
                suggested_department = parts[1].strip()
            else:
                suggested_type = result

            # Validate Case Type
            final_type = ""
            for case_type in [t[0] for t in Case.CASE_TYPES]:
                if case_type.lower() in suggested_type.lower():
                    final_type = case_type
                    break
            
            # Validate Department
            final_department = ""
            for dept in [d[0] for d in Case.DEPARTMENT_CHOICES]:
                if dept.lower() in suggested_department.lower():
                    final_department = dept
                    break
            
            return JsonResponse({'suggested_type': final_type, 'suggested_department': final_department})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)

def generate_description(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            rough_draft = data.get('rough_draft', '')
            
            if not rough_draft:
                return JsonResponse({'error': 'No text provided'}, status=400)

            prompt = (
                f"Rewrite the following cybercrime incident description into a formal 'INCIDENT REPORT' format. "
                f"Strictly follow this structure, but do NOT use any Markdown formatting (no bold **, no italics *, no headers #). "
                f"Use plain text only.\n\n"
                f"INCIDENT REPORT - [TYPE OF CRIME]\n\n"
                f"Date of Report: [Current Date]\n"
                f"Time of Report: [Current Time]\n"
                f"Reporting Party (Complainant): [Complainant's Name / ID details]\n\n"
                f"---\n\n"
                f"INCIDENT DETAILS:\n\n"
                f"Date of Incident: [Date from draft or 'Not specified']\n"
                f"Time of Incident: [Time from draft or 'Not specified']\n"
                f"Location of Incident: [Location or 'Not specified']\n"
                f"Method of Contact: [e.g., Email, SMS, Call]\n\n"
                f"NARRATIVE:\n\n"
                f"[Write a formal, detailed, and chronological narrative based on the rough draft. Use professional language.]\n\n"
                f"---\n\n"
                f"Rough Draft: {rough_draft}"
            )

            model = genai.GenerativeModel('models/gemini-2.5-flash')
            response = model.generate_content(prompt)
            refined_description = response.text.strip()
            
            return JsonResponse({'refined_description': refined_description})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def get_case_messages(request, case_id):
    case = get_object_or_404(Case, id=case_id)
    
    # Security Check: Only allow the victim who owns the case or a superuser (investigator)
    if not request.user.is_superuser and case.user != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    last_id = request.GET.get('last_id', 0)
    messages = case.messages.filter(id__gt=last_id).order_by('timestamp')
    
    # Mark messages as read if they are from the other party
    unread_messages = messages.exclude(sender=request.user)
    unread_messages.update(is_read=True)

    messages_data = [{
        'id': msg.id,
        'sender': msg.sender.username,
        'content': msg.content,
        'timestamp': msg.timestamp.strftime('%d %b %Y, %H:%M'),
        'is_current_user': msg.sender == request.user
    } for msg in messages]

    return JsonResponse({'messages': messages_data})

@login_required
def export_complaints_csv(request):
    if not request.user.is_superuser:
        return redirect('user_dashboard')

    import csv
    from django.http import HttpResponse

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="complaints_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Case ID', 'Type', 'Department', 'Status', 'Date Filed', 'Victim Name', 'Phone', 'Address', 'Description'])

    cases = Case.objects.all().order_by('-date_filed')
    for case in cases:
        # Get victim profile info safely
        phone = "N/A"
        address = "N/A"
        try:
            if hasattr(case.user, 'profile'):
                phone = case.user.profile.phone_number or "N/A"
                address = f"{case.user.profile.address}, {case.user.profile.city}"
        except:
            pass

        writer.writerow([
            case.id,
            case.case_type,
            case.department,
            case.status,
            case.date_filed.strftime('%Y-%m-%d %H:%M'),
            case.user.username,
            phone,
            address,
            case.description[:500] # Truncate long descriptions
        ])

    return response
