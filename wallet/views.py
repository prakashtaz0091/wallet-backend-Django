# views.py
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate,get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework import status
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from .serializers import UserSerializer, WalletSerializer
from drf_yasg.utils import swagger_auto_schema
# from rest_framework.permissions import AllowAny
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import Wallet
from .exceptions import InsufficientFundsError,TryingToWithdrawSavingsTooSoon
from drf_yasg import openapi



@swagger_auto_schema(method='post', request_body=UserSerializer)
@api_view(['POST'])
def registration_view(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            wallet = Wallet.objects.create(user=user)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@swagger_auto_schema(method='post', request_body=UserSerializer)
@api_view(['POST'])
def login_view(request, format=None):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            user_data = UserSerializer(user).data

            return Response({'token': token.key,'user':user_data}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)



@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'to_wallet_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'amount': openapi.Schema(type=openapi.TYPE_NUMBER),
        }
    ),
    responses={
        200: openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'message': openapi.Schema(type=openapi.TYPE_STRING),
        }),
    }
)
@api_view(['POST'])
def transfer_funds_view(request):
    # from_wallet_id = request.data.get('from_wallet')
    to_wallet_id = request.data.get('to_wallet_id')
    amount = request.data.get('amount')
    from_wallet = Wallet.objects.get(user = request.user.id)
    to_wallet = Wallet.objects.get(id=to_wallet_id)

    try:
        from_wallet.transfer_funds(to_wallet, amount)
    except InsufficientFundsError:
        return Response({'error': 'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)

    from_wallet_serializer = WalletSerializer(from_wallet)
    to_wallet_serializer = WalletSerializer(to_wallet)

    return Response({'from_wallet': from_wallet_serializer.data, 'to_wallet': to_wallet_serializer.data})


@swagger_auto_schema(method='get', responses={200: openapi.Schema(type=openapi.TYPE_OBJECT, properties={'message': openapi.Schema(type=openapi.TYPE_STRING, description='Message indicating that savings has been activated')})})
@api_view(['GET'])
def activate_saving_view(request):
    wallet = Wallet.objects.get(user = request.user.id)
    wallet.activate_saving()
    return Response({'message': 'Savings activated'})


@swagger_auto_schema(method='get', responses={200: openapi.Schema(type=openapi.TYPE_OBJECT, properties={'message': openapi.Schema(type=openapi.TYPE_STRING, description='Message indicating that savings has been deactivated')})})
@api_view(['GET'])
def deactivate_saving_view(request):
    wallet = Wallet.objects.get(user = request.user.id)
    wallet.deactivate_saving()
    return Response({'message': 'Savings deactivated'})

@swagger_auto_schema(method='get', responses={200: openapi.Schema(type=openapi.TYPE_OBJECT, properties={'message': openapi.Schema(type=openapi.TYPE_STRING, description='Savings has been trasferred to main balance')})})
@api_view(['GET'])
def withdraw_savings_view(request):
    wallet = Wallet.objects.get(user = request.user.id)
    
    try:
        wallet.withdraw_savings()
    except TryingToWithdrawSavingsTooSoon:
        return Response({'error': 'Trying to withdraw savings too soon'})
    except InsufficientFundsError:
        return Response({'error': 'Insufficient savings to withdraw'})

    return Response({'message': 'Savings withdrawn'})

# class CustomTokenObtainPairView(TokenObtainPairView):
#     permission_classes = (AllowAny,)

# class CustomTokenRefreshView(TokenRefreshView):
#     permission_classes = (AllowAny,)

# @swagger_auto_schema(method='post', request_body=UserSerializer)
# @api_view(['POST'])
# def registration_view(request):
#     if request.method == 'POST':
#         serializer = UserSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @swagger_auto_schema(method='post', request_body=UserSerializer)
# @api_view(['POST'])
# def login_view(request, format=None):
#     print("here")
#     if request.method == 'POST':
#         username = request.data.get('username')
#         password = request.data.get('password')
#         print(username,password)
#         user = authenticate(username=username, password=password)
#         if user:
#             token_view = CustomTokenObtainPairView.as_view()
#             token_data = token_view(request).data
#             return Response(token_data, status=status.HTTP_200_OK)
#         return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)  