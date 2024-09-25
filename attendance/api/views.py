from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from ..models import Attendance
from .serializers import AttendanceSerializer

class AttendanceViewSet(viewsets.ModelViewSet):
    """
    এই ViewSet-টি উপস্থিতি পরিচালনা করে এবং JWT Authentication ব্যবহার করে সুরক্ষিত।
    """
    serializer_class = AttendanceSerializer  # উপস্থিতি মডেলের সাথে সংযুক্ত Serializer
    queryset = Attendance.objects.all()  # সমস্ত উপস্থিতি তথ্য কোয়েরি করা হবে
    authentication_classes = [JWTAuthentication]  # JWT Authentication ব্যবহার করা হচ্ছে
    permission_classes = [IsAuthenticated]  # শুধুমাত্র লগ ইন করা ব্যবহারকারীরাই উপস্থিতি পরিচালনা করতে পারবে

    def get_queryset(self):
        """
        লগ ইন করা ব্যবহারকারীর কোম্পানি অনুযায়ী উপস্থিতি ডেটা ফিরিয়ে দেয়।
        """
        user = self.request.user  # লগ ইন করা ব্যবহারকারীকে নিয়ে আসা হচ্ছে
        return Attendance.objects.filter(company=user.company)  # ব্যবহারকারীর কোম্পানি অনুসারে উপস্থিতি ফিরিয়ে দিচ্ছে

    def create(self, request, *args, **kwargs):
        """
        উপস্থিতি তৈরি করার জন্য একটি কাস্টম ক্রিয়েট ফাংশন।
        এটি চেক করে ব্যবহারকারীর কোম্পানি এবং ব্যবহারকারী একটিভ কিনা।
        """
        user = request.user  # লগ ইন করা ব্যবহারকারীকে নিয়ে আসা হচ্ছে

        # চেক করা হচ্ছে ব্যবহারকারী বা তার কোম্পানি একটিভ আছে কিনা
        if not user.company.is_active or not user.is_active:
            return Response(
                {"detail": "আপনি বা আপনার কোম্পানি নিষ্ক্রিয় থাকায় উপস্থিতি প্রদান করতে পারবেন না।"},
                status=status.HTTP_403_FORBIDDEN  # নিষিদ্ধ স্ট্যাটাস রিটার্ন করা হচ্ছে
            )

        # যদি ব্যবহারকারী এবং কোম্পানি একটিভ থাকে তবে উপস্থিতি তৈরি করা হবে
        data = request.data  # অনুরোধ থেকে প্রাপ্ত ডেটা
        serializer = self.get_serializer(data=data)  # ডেটা সিরিয়ালাইজ করা হচ্ছে
        serializer.is_valid(raise_exception=True)  # ডেটা ভ্যালিড করা হচ্ছে
        self.perform_create(serializer)  # উপস্থিতি তৈরি করা হচ্ছে
        return Response(serializer.data, status=status.HTTP_201_CREATED)  # সফল সৃষ্টির পর রেসপন্স

    def perform_create(self, serializer):
        """
        উপস্থিতি তৈরি করার সময় ব্যবহারকারী এবং তার কোম্পানি সংরক্ষণ করা হয়।
        """
        serializer.save(user=self.request.user, company=self.request.user.company)  # ব্যবহারকারী এবং তার কোম্পানি সেভ করা হচ্ছে

    def update(self, request, *args, **kwargs):
        """
        উপস্থিতি আপডেট করার জন্য কাস্টম ফাংশন।
        এটি চেক করে ব্যবহারকারী বা তার কোম্পানি একটিভ আছে কিনা।
        """
        user = request.user  # লগ ইন করা ব্যবহারকারীকে নিয়ে আসা হচ্ছে

        # চেক করা হচ্ছে ব্যবহারকারী বা তার কোম্পানি একটিভ আছে কিনা
        if not user.company.is_active or not user.is_active:
            return Response(
                {"detail": "আপনি বা আপনার কোম্পানি নিষ্ক্রিয় থাকায় উপস্থিতি আপডেট করতে পারবেন না।"},
                status=status.HTTP_403_FORBIDDEN  # নিষিদ্ধ স্ট্যাটাস রিটার্ন করা হচ্ছে
            )

        partial = kwargs.pop('partial', False)  # পার্শিয়াল আপডেট কিনা যাচাই করা হচ্ছে
        instance = self.get_object()  # উপস্থিতি তথ্য নিয়ে আসা হচ্ছে
        serializer = self.get_serializer(instance, data=request.data, partial=partial)  # ডেটা সিরিয়ালাইজ করা হচ্ছে
        serializer.is_valid(raise_exception=True)  # ডেটা ভ্যালিড করা হচ্ছে
        self.perform_update(serializer)  # উপস্থিতি আপডেট করা হচ্ছে
        return Response(serializer.data)  # আপডেটকৃত উপস্থিতি তথ্য রিটার্ন করা হচ্ছে

    def perform_update(self, serializer):
        """
        উপস্থিতি আপডেট করার সময় চেক আউট টাইম এবং অন্যান্য তথ্য সংরক্ষণ করা হচ্ছে।
        """
        serializer.save()  # আপডেটকৃত উপস্থিতি সেভ করা হচ্ছে
