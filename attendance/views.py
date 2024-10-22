from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render,redirect
from .models import AttendanceLog,Employee
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@staff_member_required  # Ensure only staff members (admin users) can access this view
def schedule_report_view(request):
    # এই ভিউতে আপনি কাস্টম ডাটা প্রক্রিয়া করতে পারেন
    return render(request, 'admin/schedule_report.html', context={})



@login_required
def give_attendance_view(request):
    if request.method == 'POST':
        # Extracting latitude, longitude, and location_name from the form
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        location_name = request.POST.get('location_name')

        # Get the current user's company
        company = request.user.company  # Assuming the user has a company field
        
        # Get the employee linked with the current user
        try:
            # First filter employees by the company
            employees_in_company = Employee.objects.filter(company=company)
            # Then find the employee linked to the current user
            employee = employees_in_company.get(user=request.user)

            
            # Now you can proceed to create the attendance log
            attendance_log = AttendanceLog.objects.create(
                employee=employee,
                latitude=latitude,
                longitude=longitude,
                locationName=location_name,
                company=company,
                verification_method='GPS'
                # Add other fields as necessary
            )
            # Redirect or return a response as needed
            return redirect('index')  # Change this to your desired redirect
        except Employee.DoesNotExist:
            # Handle the case where the employee is not found
            return render(request, 'error.html', {'message': 'Employee not found.'})
        except Exception as e:
            # Handle any other exceptions
            return render(request, 'error.html', {'message': str(e)})

    # Handle GET request
    return render(request, 'give-attendance.html')  # Render your attendance form
