# from .models import Booking
# from rest_framework import serializers
# from django.utils import timezone
#
#
# #-----------------------------------------------------------------------------------------------------------------------
#
#
# class BookingListSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Booking
#         fields = ['id', 'owner', 'title', 'description', 'status', 'deadline', ]
#
#
# class TaskCreateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Task
#         fields = ['title', 'owner', 'description', 'status', 'deadline',]
#         read_only_fields = ['owner']
#
#
#     def validate_deadline(self, value):
#         if value < timezone.now():
#             raise serializers.ValidationError('Deadline can`t be in past')
#         return value