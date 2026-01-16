from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('investigator/', views.investigator_dashboard, name='investigator_dashboard'),
    path('investigator/all-complaints/', views.all_complaints, name='all_complaints'),
    path('user/', views.user_dashboard, name='user_dashboard'),
    
    # New URLs for the functions we added
    path('file-report/', views.file_report, name='file_report'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('case/<int:case_id>/', views.case_detail, name='case_detail'),
    path('update-case/<int:case_id>/', views.update_case_status, name='update_case_status'),
        
    # This is the new path for your chatbot's backend API
    path('chatbot/', views.chatbot_response, name='chatbot_response'),

    # Authentication
    path('accounts/', include('django.contrib.auth.urls')),
    path('signup/', views.signup, name='signup'),

    # AI Features
    path('predict-case-type/', views.predict_case_type, name='predict_case_type'),
    path('generate-description/', views.generate_description, name='generate_description'),
    path('case/<int:case_id>/messages/', views.get_case_messages, name='get_case_messages'),
    path('api/heatmap-data/', views.get_heatmap_data, name='get_heatmap_data'),
    path('investigator/export-complaints/', views.export_complaints_csv, name='export_complaints_csv'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# from django.urls import path
# from . import views

# urlpatterns = [
#     # This will be your new homepage
#     path('', views.home, name='home'),
    
#     # Path for the investigator dashboard
#     path('investigator/', views.investigator_dashboard, name='investigator_dashboard'),
    
#     # Path for the user dashboard
#     path('user/', views.user_dashboard, name='user_dashboard'),
# ]

