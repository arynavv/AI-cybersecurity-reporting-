from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"Profile for {self.user.username}"

class Case(models.Model):
    CASE_TYPES = [
        ("UPI Fraud", "UPI Fraud"),
        ("Online Banking Fraud", "Online Banking Fraud"),
        ("Credit/Debit Card Fraud", "Credit/Debit Card Fraud"),
        ("Unauthorized Bank Transfer", "Unauthorized Bank Transfer"),
        ("Investment Scam", "Investment Scam"),
        ("Online Shopping Fraud", "Online Shopping Fraud"),
        ("Loan App Scam", "Loan App Scam"),

        ("Phishing", "Phishing"),
        ("Spear Phishing", "Spear Phishing"),
        ("Email Spoofing", "Email Spoofing"),
        ("Business Email Compromise", "Business Email Compromise"),

        ("Identity Theft", "Identity Theft"),
        ("SIM Swapping", "SIM Swapping"),
        ("Impersonation", "Impersonation"),

        ("Cyberstalking", "Cyberstalking"),
        ("Cyberbullying", "Cyberbullying"),
        ("Account Hacked", "Account Hacked"),
        ("Revenge Porn", "Revenge Porn"),

        ("Data Breach", "Data Breach"),
        ("Ransomware", "Ransomware"),
        ("Malware Attack", "Malware Attack"),
        ("Insider Attack", "Insider Attack"),

        ("Government Portal Hacked", "Government Portal Hacked"),
        ("Public Service Disruption", "Public Service Disruption"),
        ("Infrastructure Attacks", "Infrastructure Attacks"),

        ("Phone Cloning", "Phone Cloning"),
        ("Mobile Spyware", "Mobile Spyware"),
        ("Malicious Apps", "Malicious Apps"),

        ("IoT Device Hacking", "IoT Device Hacking"),
        ("Smart Home Intrusion", "Smart Home Intrusion"),
        ("CCTV Hacking", "CCTV Hacking"),
        ("Cloud Account Hacking", "Cloud Account Hacking"),
        ("Cloud Server Breach", "Cloud Server Breach"),

        ("Cyber Terrorism", "Cyber Terrorism"),
        ("Cyber Espionage", "Cyber Espionage"),
        ("Dark Web Threat", "Dark Web Threat"),

        ("Blackmailing", "Blackmailing"),
        ("Online Threat", "Online Threat"),
        ("Unknown Malware", "Unknown Malware"),
        ("Piracy", "Piracy"),
        ("Vehicle GPS Hacking", "Vehicle GPS Hacking"),
        ("Industrial Machine Hacking", "Industrial Machine Hacking"),

        ("Other", "Other"),
    ]

    DEPARTMENT_CHOICES = [
        ('Financial Cyber Crime', 'Financial Cyber Crime'),
        ('Social Media Crime', 'Social Media Crime'),
        ('E-commerce & Online Fraud', 'E-commerce & Online Fraud'),
        ('Government & Critical Infrastructure Attacks', 'Government & Critical Infrastructure Attacks'),
        ('Corporate / Business Cyber Crime', 'Corporate / Business Cyber Crime'),
        ('Healthcare Cyber Crime', 'Healthcare Cyber Crime'),
        ('Education Sector Crime', 'Education Sector Crime'),
        ('Telecommunication Crime', 'Telecommunication Crime'),
        ('Entertainment & Copyright Crime', 'Entertainment & Copyright Crime'),
        ('Transportation & Automotive Cyber Crime', 'Transportation & Automotive Cyber Crime'),
        ('IoT / Smart Device Cyber Crime', 'IoT / Smart Device Cyber Crime'),
        ('Cloud Cyber Crime', 'Cloud Cyber Crime'),
        ('Cryptocurrency / Blockchain Crime', 'Cryptocurrency / Blockchain Crime'),
        ('Mobile-Based Cyber Crime', 'Mobile-Based Cyber Crime'),
        ('Email & Communication Crime', 'Email & Communication Crime'),
        ('Cyber Terrorism', 'Cyber Terrorism'),
        ('Cyber Espionage', 'Cyber Espionage'),
        ('Personal Cyber Crime', 'Personal Cyber Crime'),
        ('Dark Web Crime', 'Dark Web Crime'),
        ('Industrial/Manufacturing Cyber Crime', 'Industrial/Manufacturing Cyber Crime'),
    ]
    
    STATUS_CHOICES = [
        ('Submitted', 'Submitted'),
        ('Under Review', 'Under Review'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    case_type = models.CharField(max_length=50, choices=CASE_TYPES)
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES, blank=True, null=True)
    description = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Submitted')
    date_filed = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Case #{self.id} - {self.case_type} by {self.user.username}"

class Message(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender.username} on Case #{self.case.id}"

class Evidence(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='evidence')
    file = models.FileField(upload_to='evidence/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Evidence for Case #{self.case.id} - {self.file.name}"