from django.shortcuts import render, get_object_or_404
from apps.employees.models import Employee


def detalle_empleado(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    return render(request, 'attendance/employee_detail.html', {
        'employee': employee,
    })


def historial(request):
    return render(request, 'attendance/history.html')
