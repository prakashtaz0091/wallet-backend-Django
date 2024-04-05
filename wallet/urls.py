# urls.py

from django.urls import path
# from .views import registration_view, login_view
from .views import registration_view, login_view,transfer_funds_view,activate_saving_view,deactivate_saving_view,withdraw_savings_view    
# ,CustomTokenObtainPairView,CustomTokenRefreshView

urlpatterns = [
    path('register/', registration_view, name='register'),
    path('login/', login_view, name='login'),
    path('transfer-funds/', transfer_funds_view, name='transfer-funds'),
    path('activate-saving/', activate_saving_view, name='activate-saving'),
    path('deactivate-saving/', deactivate_saving_view, name='deactivate-saving'),
    path('withdraw-saving/', withdraw_savings_view, name='withdraw-saving'),
    # path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    
]
