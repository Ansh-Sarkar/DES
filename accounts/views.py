from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from .serializer import *
from datetime import datetime
from .emails import *

from django.views.decorators.csrf import csrf_exempt

OTP_DICTIONARY = {}
OTP_EXPIRE_TIME = 5 * 60

class RegisterUser(APIView):
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

class GenerateOTP(APIView):
    def post(self, request):
        try:
            data = request.data
            print("c1")
            OTP_DICTIONARY[data['email']] = (
                send_otp_via_email(data['email']),
                datetime.now()
            )
            print('c2')
            return Response({
                'status': 200,
                'message': 'OTP Generated Succesfully',
            })
        
        except Exception as error:
            print(error)
            print('c3')
            return Response({
                'status': 400,
                'message': 'something went wrong',
                'data': str(error)
            })

class VerifyOTP(APIView):
    def post(self, request):
        try:
            data = request.data
            email = data['email']
            otp = data['otp']
            time_elapsed = (datetime.now() - OTP_DICTIONARY[email][1]).total_seconds()
            
            if time_elapsed > OTP_EXPIRE_TIME or str(otp) != str(OTP_DICTIONARY[email][0]):
                OTP_DICTIONARY[email] = None
                return Response({
                    'status': 400,
                    'verified': False,
                    'message': 'OTP has either expired or is invalid',
                })
            else:
                OTP_DICTIONARY[email] = None
                return Response({
                    'status': 200,
                    'verified': True,
                    'message': 'OTP was successfully verified !'
                })

        except Exception as error:
            print(error)
            return Response({
                'status': 400,
                'message': 'Oops ! Try generating a new OTP.',
                'data': str(error)
            })


class VerifyUser(APIView):
    def post(self, request):
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