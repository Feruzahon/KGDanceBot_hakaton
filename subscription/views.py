from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import Subscription
from .serializers import SubscriptionSerializer
from .tasks import check_subscription_expiry
    
class CreateSubView(APIView):
    def post(self, request):
        serializer = SubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class GetMySubView(APIView):
    def get(self, request):
        subscriptions = Subscription.objects.filter(user=request.user)
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data, status=200)
    
class GetChildSubView(APIView):   
    def get(self, request):
        children = request.user.children.all()
        child_ids = children.values_list('id', flat=True)
        subscriptions = Subscription.objects.filter(user__in=child_ids)
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data, status=200)
    
class GetUserSubView(APIView):
    def get(self, request, user_id):
        subscriptions = Subscription.objects.filter(user=user_id)
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data, status=200)


@api_view(['PATCH'])
def mark_attendance(request, subscription_id):
    sub = Subscription.objects.get(id=subscription_id)
    date = request.data.get('date')
    status = request.data.get('status')

    attendance = sub.attendance or {}
    attendance[date] = bool(status)
    sub.attendance = attendance

    sub.used_lessons = sum(1 for s in attendance.values() if s)
    sub.save()
    check_subscription_expiry.delay(sub.id)
    check_and_delete_sub(sub.id)
    return Response({'message': 'Attendance updated', 'attendance': sub.attendance, 'total_lessons':sub.total_lessons})

def check_and_delete_sub(sub_id):
    sub = Subscription.objects.get(id=sub_id)
    if len(sub.attendance) == sub.total_lessons:
        sub.delete()

class DeleteSubView(APIView):
    def delete(self, request, sub_id):
        sub = Subscription.objects.get(id=sub_id)
        sub.delete()
        return Response({"detail":"Group deleted"})

    
