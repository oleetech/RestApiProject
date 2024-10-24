from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from .models import Company 
CustomUser = get_user_model()
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache

class CustomUserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'mobileNo','company' )}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'mobileNo', 'company', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}
        ),
    )
    list_display = ('username', 'email', 'mobileNo', 'is_staff','company')
    search_fields = ('username', 'email', 'mobileNo')
    filter_horizontal = ('groups', 'user_permissions',)

class CustomGroupAdmin(GroupAdmin):  # Inherits from GroupAdmin
    filter_horizontal = ('permissions',)

# Register the Permission model in the admin panel
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'codename', 'content_type']
    search_fields = ['name', 'codename']
    list_filter = ['content_type']

# Unregister the default Group admin
admin.site.unregister(Group)

# Register your CustomUserAdmin with the admin site
admin.site.register(CustomUser, CustomUserAdmin)

# Register your CustomGroupAdmin with the admin site
admin.site.register(Group, CustomGroupAdmin)
# Register the Permission model in the admin site
admin.site.register(Permission, PermissionAdmin)


# Admin class for Company model
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')  # Fields to display in the list view
    search_fields = ('name',)  # Searchable fields in the admin interface
    # Define fieldsets for detail view and editing
    fieldsets = (
        ("Company Information", {
            'fields': ('name', 'address', 'logo','employee_limit')
        }),
        ('Limits', {
            'fields': ('is_active', 'subscription',),
            'classes': ('wide',)  # Make this section collapsible
        }),
    )

    # Customizing the form for adding and changing Company
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        # Custom logic can be added here if necessary
        return super().formfield_for_dbfield(db_field, request, **kwargs)

        

    # Override save_model to cache the saved Company object
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Invalidate the cache when a company is added or updated
        cache.delete('all_companies')

    # Override delete_model to invalidate cache when a company is deleted
    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        # Invalidate the cache when a company is deleted
        cache.delete('all_companies')

    # Override get_queryset to cache the list of all Company objects
    def get_queryset(self, request):
        companies = cache.get('all_companies')
        if companies:
            # Print that the data is fetched from Redis
            # print("Companies loaded from Redis cache.")
            pass
        else:
            # Print that the data is fetched from the database
            # print("Companies loaded from the database.")
            companies = super().get_queryset(request)
            cache.set('all_companies', companies, timeout=600)
        return companies
    
# Register the Company model with the admin site
admin.site.register(Company, CompanyAdmin)

from .models import Subscription

class SubscriptionAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('name', 'price', 'max_employees', 'max_storage', 'advanced_features')

    # Searchable fields in the admin interface
    search_fields = ('name',)

    # Filters for the list view
    list_filter = ('name', 'advanced_features')

    # Default ordering in the admin list view
    ordering = ('-price',)  # Display by price descending order

    # Customization of how fields are grouped in the form view (for a structured layout)
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'price'),
            'classes': ('wide',),  # 'wide' is a built-in CSS class for width
        }),
        ('Features', {
            'fields': ('max_employees', 'max_storage', 'advanced_features'),
            'classes': ('wide',),  # Same here
        }),
    )

# একটি কাস্টম অ্যাকশন যুক্ত করা হচ্ছে
actions = ['set_to_free_subscription']  
# এখানে 'actions' নামে একটি লিস্ট তৈরি করা হয়েছে, যেখানে 'set_to_free_subscription' নামে একটি অ্যাকশন যুক্ত করা হয়েছে।
# অ্যাকশনটি অ্যাডমিন প্যানেলের ড্রপডাউন মেনুতে প্রদর্শিত হবে।
# প্রতিবার নতুন অ্যাকশন যুক্ত করলে এর জন্য একই নামে একটি ফাংশন তৈরি করতে হবে।
# 'set_to_free_subscription' অ্যাকশনের মাধ্যমে নির্বাচিত সাবস্ক্রিপশনগুলোর উপর কাজ করা হবে।

# সিলেক্ট করা সাবস্ক্রিপশনগুলোকে 'Free' প্ল্যানে সেট করার জন্য কাস্টম অ্যাকশন তৈরি
def set_to_free_subscription(self, request, queryset):
    # 'queryset' হলো নির্বাচিত সাবস্ক্রিপশনগুলোর তালিকা।
    # queryset.update(name='Free', price=0.00) মেথডটি নির্বাচন করা সাবস্ক্রিপশনগুলোর 'name' এবং 'price' আপডেট করবে।
    
    # 'name' ফিল্ডকে 'Free' এবং 'price' ফিল্ডকে 0.00 এ আপডেট করা হবে।
    queryset.update(name='Free', price=0.00)  
    # ১. নির্বাচিত প্রতিটি সাবস্ক্রিপশনের 'name' ফিল্ডকে 'Free' করা হচ্ছে।
    # ২. নির্বাচিত প্রতিটি সাবস্ক্রিপশনের 'price' ফিল্ডকে 0.00 এ সেট করা হচ্ছে, অর্থাৎ সাবস্ক্রিপশনটি বিনামূল্যে করা হচ্ছে।

    # self.message_user(request, "Selected subscriptions are set to 'Free'.") 
    # এই ফাংশনটি অ্যাডমিন ইউজারকে একটি সফলতার মেসেজ পাঠাবে।
    # মেসেজটি অ্যাডমিন প্যানেলের উপরের দিকে প্রদর্শিত হবে।
    self.message_user(request, "Selected subscriptions are set to 'Free'.")
    # এখানে "Selected subscriptions are set to 'Free'." মেসেজটি দেখানো হবে, যাতে অ্যাডমিন ইউজার জানতে পারে 
    # যে নির্বাচিত সাবস্ক্রিপশনগুলো সফলভাবে 'Free' এ আপডেট হয়েছে।

# অ্যাকশনের জন্য বর্ণনা (description) যা অ্যাডমিন প্যানেলের ড্রপডাউন মেনুতে প্রদর্শিত হবে।
set_to_free_subscription.short_description = "Set selected subscriptions to Free plan"
# 'set_to_free_subscription' এর জন্য একটি short_description সেট করা হয়েছে, যা ড্রপডাউন মেনুতে
# "Set selected subscriptions to Free plan" হিসেবে দেখাবে।



# Register the Subscription model with the admin site
admin.site.register(Subscription, SubscriptionAdmin)


