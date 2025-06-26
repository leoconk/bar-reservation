from datetime import timedelta, datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.urls import reverse
from django.http import HttpResponseBadRequest
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Reservation, Table
from .forms import ReservationForm, TableForm, StaffUserCreationForm


def homepage(request):
    if request.user.is_authenticated:
        return render(request, 'reservations/homepage.html', {
            'user': request.user
        })

    login_form = AuthenticationForm()
    register_form = StaffUserCreationForm()
    return render(request, 'reservations/homepage.html', {
        'login_form': login_form,
        'register_form': register_form
    })


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, "Inicio de sesión exitoso.")
            return redirect('table_grid')
        else:
            messages.error(request, "Nombre de usuario o contraseña incorrectos.")
    return redirect('homepage')


def logout_view(request):
    logout(request)
    messages.info(request, "Sesión cerrada.")
    return redirect('homepage')


def create_user(request):
    if request.method == 'POST':
        form = StaffUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            user.save()
            login(request, user)
            messages.success(request, "Cuenta creada exitosamente.")
            return redirect('table_grid')
        else:
            messages.error(request, "Error al crear la cuenta. Intenta nuevamente.")
    return redirect('homepage')


@login_required
def table_list(request):
    tables = Table.objects.all().order_by('id')
    form = TableForm()
    return render(request, 'reservations/tablelist.html', {'tables': tables, 'form': form})


@login_required
def table_create(request):
    if request.method == 'POST':
        form = TableForm(request.POST)
        if form.is_valid():
            form.save()
    return redirect('table_list')


@login_required
def table_delete(request, pk):
    table = get_object_or_404(Table, pk=pk)
    if request.method == 'POST':
        table.delete()
    return redirect('table_list')


@login_required
def table_update(request, pk):
    table = get_object_or_404(Table, pk=pk)
    if request.method == 'POST':
        form = TableForm(request.POST, instance=table)
        if form.is_valid():
            form.save()
            return redirect('table_list')
    else:
        form = TableForm(instance=table)
    return render(request, 'reservations/table_form.html', {'form': form})


@login_required
def table_grid(request):
    date_str = request.GET.get('date')
    selected_date = timezone.localdate()
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    tables = Table.objects.all().order_by('id')
    table_status = {}

    for table in tables:
        reservations = Reservation.objects.filter(
            user=request.user,
            table=table,
            start_time__date=selected_date
        ).order_by('start_time')

        table_status[table] = {
            'status': "Reserved" if reservations.exists() else "Disponible",
            'reservations': reservations
        }

    return render(request, 'reservations/reservations_grid.html', {
        'table_status': table_status,
        'selected_date': selected_date,
        'tables': tables,
        'form': ReservationForm()
    })


@login_required
def reservation_create(request):
    if request.method == 'POST':
        table_id = request.POST.get('table')
        name = request.POST.get('name')
        hour = request.POST.get('hour')
        status = request.POST.get('status')
        date = request.POST.get('date')

        if not table_id or not hour or not date:
            return HttpResponseBadRequest("Missing fields.")

        try:
            start_time = datetime.strptime(f"{date} {hour}", "%Y-%m-%d %H:%M")
        except ValueError:
            return HttpResponseBadRequest("Invalid date or time format.")

        table = get_object_or_404(Table, pk=table_id)

        reservation = Reservation(
            user=request.user,
            table=table,
            name=name,
            start_time=start_time,
            end_time=start_time + timedelta(hours=1),
            status=status
        )
        reservation.full_clean()
        reservation.save()

        return redirect(f"{reverse('table_grid')}?date={start_time.date()}")

    return redirect('table_grid')


@login_required
def reservation_update(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            updated_reservation = form.save(commit=False)
            updated_reservation.end_time = updated_reservation.start_time + timedelta(hours=1)
            updated_reservation.save()
            return redirect('table_grid')
    else:
        form = ReservationForm(instance=reservation)
    return render(request, 'reservations/reservation_form.html', {'form': form})


@login_required
def reservation_delete(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)
    if request.method == 'POST':
        reservation.delete()
    return redirect('table_grid')
