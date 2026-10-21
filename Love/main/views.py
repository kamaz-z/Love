from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import MomentForm
from .models import BucketItem, Moment, MomentPhoto

@login_required(login_url='login')
def Moment_form(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        moment_form = MomentForm(request.POST, request.FILES)
        if moment_form.is_valid():
            moment = moment_form.save()
            for image in moment_form.cleaned_data['additional_images']:
                MomentPhoto.objects.create(moment=moment, image=image)
            messages.success(request, 'Спогад успішно збережено!')
            return redirect('moment_detail', moment_id=moment.pk)
    else:
        moment_form = MomentForm()

    return render(request, 'forms.html', {'moment_form': moment_form})

def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect('moments_list')
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect(request.GET.get('next') or 'moments_list')
    return render(request, 'login.html', {'login_form': form})


@require_POST
def register(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect('moments_list')

    user_model = get_user_model()
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '')
    password_confirmation = request.POST.get('password_confirmation', '')
    if request.method != 'POST':
        return redirect('login')
    if not username or not password or not password_confirmation:
        messages.error(request, 'Заповніть логін і обидва поля пароля.')
        return redirect('login')
    if password != password_confirmation:
        messages.error(request, 'Паролі не збігаються.')
        return redirect('login')
    if user_model.objects.filter(username=username).exists():
        messages.error(request, 'Такий логін уже зайнятий.')
        return redirect('login')

    user = user_model(username=username)
    try:
        validate_password(password, user=user)
    except ValidationError as error:
        for error_message in error.messages:
            messages.error(request, error_message)
        return redirect('login')

    user.set_password(password)
    user.save()
    login(request, user)
    return redirect('moments_list')


@login_required(login_url='login')
def moments_list(request: HttpRequest) -> HttpResponse:
    selected_period = request.GET.get('period', '0-3')
    selected_category = request.GET.get('category', 'all')
    valid_periods = {value for value, _label in Moment.PERIOD_CHOICES}
    valid_categories = {value for value, _label in Moment.CATEGORY_CHOICES}

    if selected_period not in valid_periods and selected_period != 'all':
        selected_period = '0-3'
    if selected_category != 'all' and selected_category not in valid_categories:
        selected_category = 'all'

    moments = Moment.objects.all()
    if selected_period != 'all':
        moments = moments.filter(period=selected_period)
    if selected_category != 'all':
        moments = moments.filter(category=selected_category)

    return render(
        request,
        'index.html',
        {
            'moments': moments.order_by('-date', '-created_at'),
            'selected_period': selected_period,
            'selected_category': selected_category,
        },
    )


@login_required(login_url='login')
def comic_story(request: HttpRequest) -> HttpResponse:
    return render(request, 'comix.html')


@login_required(login_url='login')
def moment_detail(request: HttpRequest, moment_id: int) -> HttpResponse:
    moment = get_object_or_404(Moment, pk=moment_id)
    return render(request, 'moment_detail.html', {'moment': moment})


@login_required(login_url='login')
def bucket_list(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        'bucket_list.html',
        {'bucket_items': BucketItem.objects.order_by('is_completed', '-created_at')},
    )


@login_required(login_url='login')
@require_POST
def add_bucket_item(request: HttpRequest) -> HttpResponse:
    title = request.POST.get('title', '').strip()
    if not title:
        messages.error(request, 'Введіть назву ідеї.')
    elif len(title) > 255:
        messages.error(request, 'Назва ідеї має містити не більше 255 символів.')
    else:
        BucketItem.objects.create(title=title)
        messages.success(request, 'Ідею додано до банки!')
    return redirect('bucket_list')


@login_required(login_url='login')
@require_POST
def toggle_bucket_item(_request: HttpRequest, item_id: int) -> HttpResponse:
    item = get_object_or_404(BucketItem, pk=item_id)
    item.is_completed = not item.is_completed
    item.save(update_fields=['is_completed'])
    return redirect('bucket_list')


@login_required(login_url='login')
def random_moment(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        'random.moment.html',
        {'random_moment': Moment.objects.order_by('?').first()},
    )
