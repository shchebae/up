from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Request, Category
from .forms import RequestForm, RequestStatusForm

def is_admin(user):
    return user.is_superuser or user.is_staff

@login_required
def request_list(request):
    if is_admin(request.user):
        requests = Request.objects.all()
    else:
        requests = Request.objects.filter(user=request.user)
    return render(request, 'requests/request_list.html', {'requests': requests})

@login_required
def request_create(request):
    if request.method == 'POST':
        form = RequestForm(request.POST, request.FILES)
        if form.is_valid():
            request_obj = form.save(commit=False)
            request_obj.user = request.user
            request_obj.save()
            messages.success(request, 'Заявка успешно создана')
            return redirect('request_list')
    else:
        form = RequestForm()
    return render(request, 'requests/request_form.html', {'form': form})

@login_required
def request_detail(request, pk):
    request_obj = get_object_or_404(Request, pk=pk)
    if not is_admin(request.user) and request.user != request_obj.user:
        messages.error(request, 'У вас нет доступа к этой заявке')
        return redirect('request_list')
    
    status_form = None
    if is_admin(request.user):
        if request.method == 'POST':
            status_form = RequestStatusForm(request.POST, instance=request_obj)
            if status_form.is_valid():
                status_form.save()
                messages.success(request, 'Статус заявки обновлен')
                return redirect('request_list')
        else:
            status_form = RequestStatusForm(instance=request_obj)
    
    return render(request, 'requests/request_detail.html', {
        'request': request_obj,
        'status_form': status_form,
    })

@user_passes_test(is_admin)
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'requests/category_list.html', {'categories': categories})

@user_passes_test(is_admin)
def category_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Category.objects.create(name=name)
            messages.success(request, 'Категория создана')
        return redirect('category_list')
    return render(request, 'requests/category_form.html')
