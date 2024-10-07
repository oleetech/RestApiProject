from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from .models import Company 
CustomUser = get_user_model()
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _

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

# Unregister the default Group admin
admin.site.unregister(Group)

# Register your CustomUserAdmin with the admin site
admin.site.register(CustomUser, CustomUserAdmin)

# Register your CustomGroupAdmin with the admin site
admin.site.register(Group, CustomGroupAdmin)


# Admin class for Company model
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')  # Fields to display in the list view
    search_fields = ('name',)  # Searchable fields in the admin interface
    actions = ['activate_company', 'deactivate_company']  # Registering custom actions

    def activate_company(self, request, queryset):
        # Check if the user has the 'activate_company' permission
        if not request.user.has_perm('authentication.activate_company'):
            raise PermissionDenied("You do not have permission to activate companies.")
        
        # Activate the selected companies
        queryset.update(is_active=True)
        self.message_user(request, _("Selected companies have been activated."))

    def deactivate_company(self, request, queryset):
        # Check if the user has the 'deactivate_company' permission
        if not request.user.has_perm('authentication.deactivate_company'):
            raise PermissionDenied("You do not have permission to deactivate companies.")
        
        # Deactivate the selected companies
        queryset.update(is_active=False)
        self.message_user(request, _("Selected companies have been deactivated."))

    # Action display names
    activate_company.short_description = _("Activate selected companies")
    deactivate_company.short_description = _("Deactivate selected companies")

# Register the Company model with the admin site
admin.site.register(Company, CompanyAdmin)