from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from ..models import Company, CustomUser

User = get_user_model()

class CompanySerializer(serializers.ModelSerializer):

    
    class Meta:
        model = Company
        fields = ['id', 'name', 'address', 'is_active']




class RegisterSerializer(serializers.ModelSerializer):
    # Meta ক্লাসের মধ্যে আমরা মডেল এবং ক্ষেত্রগুলো নির্ধারণ করছি
    class Meta:
        model = CustomUser  # আমরা যে মডেলটি ব্যবহার করছি তা হলো CustomUser
        fields = ['id', 'email', 'username', 'mobileNo', 'company', 'password']  # প্রয়োজনীয় ক্ষেত্রগুলো
    
    def validate_email(self, value):
        """
        Validate that the email is unique.
        """
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError(_("This email is already in use."))  # এই ইমেইল ইতিমধ্যেই ব্যবহৃত হচ্ছে
        return value

    def create(self, validated_data):
        # company ফিল্ডটি validated_data থেকে অপসারণ করা হচ্ছে
        company = validated_data.pop('company', None)  # company ফিল্ডের মানটি সংরক্ষণ করছি

        # যদি company দেওয়া হয় তবে তা যাচাই করা হচ্ছে
        if company:
            # কোম্পানি অবজেক্ট খুঁজে বের করা হচ্ছে
            company_instance = Company.objects.filter(id=company.id).first()  # কোম্পানি অবজেক্টটি পাওয়া গেলে
            # যদি কোম্পানির is_active ফিল্ডটি False হয়, তবে ইউজার তৈরি করা যাবে না
            if company_instance and not company_instance.is_active:
                raise serializers.ValidationError(_("This company is not active."))  # ValidationError তোলা হচ্ছে

        # 'password' ফিল্ডটি validated_data থেকে অপসারিত করা হচ্ছে এবং এর মানটি 'password' ভেরিয়েবলে সংরক্ষণ করা হচ্ছে
        password = validated_data.pop('password')  # পাসওয়ার্ডকে নিরাপদে প্রক্রিয়া করার জন্য অপসারণ করা হচ্ছে

        # ইউজার অবজেক্ট তৈরি করা হচ্ছে
        user = CustomUser(**validated_data)  # ইউজার অবজেক্ট তৈরি হচ্ছে

        # ইউজারের পাসওয়ার্ড সেট করা হচ্ছে
        user.set_password(password)  # পাসওয়ার্ড সেট করা হচ্ছে

        # ইউজার অবজেক্টটি ডাটাবেসে সংরক্ষণ করা হচ্ছে
        user.save()  # ইউজারটি ডাটাবেসে সংরক্ষিত হচ্ছে

        # company যদি None হয় তবে তা ইউজারের company ফিল্ডে সংযুক্ত করা হচ্ছে
        if company:
            user.company = company_instance  # কোম্পানি সংযুক্ত করা হচ্ছে
            user.save()  # আবার ইউজারটি সংরক্ষণ করা হচ্ছে

        return user  # তৈরি করা ইউজার অবজেক্টটি ফেরত দেওয়া হচ্ছে

    def update(self, instance, validated_data):
        # company ফিল্ডটি validated_data থেকে অপসারণ করা হচ্ছে
        company = validated_data.pop('company', None)  # company ফিল্ডের মানটি সংরক্ষণ করছি

        # যদি company দেওয়া হয় তবে তা যাচাই করা হচ্ছে
        if company:
            # কোম্পানি অবজেক্ট খুঁজে বের করা হচ্ছে
            company_instance = Company.objects.filter(id=company.id).first()  # কোম্পানি অবজেক্টটি পাওয়া গেলে
            # যদি কোম্পানির is_active ফিল্ডটি False হয়, তবে আপডেট করা যাবে না
            if company_instance and not company_instance.is_active:
                raise serializers.ValidationError(_("This company is not active."))  # ValidationError তোলা হচ্ছে

        # ইউজারের অন্য ক্ষেত্রগুলো আপডেট করা হচ্ছে
        for attr, value in validated_data.items():
            setattr(instance, attr, value)  # বর্তমান অবজেক্টের গুণাবলী আপডেট করা হচ্ছে

        # company ফিল্ডটি আপডেট করা হচ্ছে যদি এটি দেওয়া থাকে
        if company:
            instance.company = company_instance  # কোম্পানি আপডেট করা হচ্ছে

        instance.save()  # আপডেট হওয়া ইউজারটি ডাটাবেসে সংরক্ষিত হচ্ছে
        return instance  # আপডেট হওয়া ইউজার অবজেক্টটি ফেরত দেওয়া হচ্ছে
