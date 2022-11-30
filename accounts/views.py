from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from .serializer import *
from .emails import *

from django.views.decorators.csrf import csrf_exempt


class RegisterAPI(APIView):
    def post(self, request):
        try:
            data = request.data
            serializer = UserSerializer(data = data)
            if serializer.is_valid():
                serializer.save()
                send_otp_via_email(serializer.data['email'])
                return Response({
                    'status': 200,
                    'message': 'registration successful. kindly check your email',
                    'data': serializer.data,
                })
            return Response({
                'status': 400,
                'message': 'something went wrong',
                'data': serializer.errors
            })

        except Exception as error:
            print(error)
            return Response({
                'status': 400,
                'message': 'something went wrong',
                'data': 'server error'
            })

class VerifyOTP(APIView):
    def post(self, request):
        print("reached here aaaaaaaaaaaaaaaaa")
        try:
            data = request.data
            serializer = VerifyAccountSerializer(data = data)

            if serializer.is_valid():
                email = serializer.data['email']
                otp = serializer.data['otp']

                print("Obtained the OTP :", otp)

                user = User.objects.filter(email = email)
                if not user.exists():
                    return Response({
                        'status': 400,
                        'message': 'something went wrong',
                        'data': 'invalid email'
                    })
                
                user = user[0]
                if user.otp != otp:
                    return Response({
                        'status': 400,
                        'message': 'something went wrong',
                        'data': 'wrong otp'
                    })

                print("user[0] before :", user.is_verified)
                user.is_verified = True
                user.save()
                print("user[0] after :", user.is_verified)

                return Response({
                    'status': 200,
                    'message': 'account verified',
                    'data': serializer.data,
                })
            
            return Response({
                'status': 400,
                'message': 'something went wrong',
                'data': serializer.errors
            })

        except Exception as error:
            print(error)
            return Response({
                'status': 400,
                'message': 'something went wrong',
                'data': serializer.errors
            })