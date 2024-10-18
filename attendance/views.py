from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

@staff_member_required  # Ensure only staff members (admin users) can access this view
def schedule_report_view(request):
    # এই ভিউতে আপনি কাস্টম ডাটা প্রক্রিয়া করতে পারেন
    return render(request, 'admin/schedule_report.html', context={})
