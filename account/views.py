from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from account.forms import (LoginForm, UserRegistrationForm,
                           UserEditForm, ProfileEditForm)
from account.models import Profile, Contact
from django.views.decorators.http import require_POST
from common.decorators import ajax_required, self_view_not_allowed
from actions.utils import create_action
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from actions.models import Action


# Create your views here.
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            username = form_data['username']
            password = form_data['password']
            import pdb;
            pdb.set_trace()
            user = authenticate(request, username=username,
                                password=password)
            message = 'Invalid Login'
            if user is not None:
                if user.is_active:
                    login(request, user)
                    message = 'Authenticated Successfully'
                else:
                    message = 'User is not active'

            return HttpResponse(message)
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})


@login_required
def dashboard(request):
    # Display all actions by Default
    actions = Action.objects.exclude(user=request.user)
    following_ids = request.user.following.values_list('id', flat=True)

    # User is following others, retrieve their actions only
    # if following_ids:
    #     actions = actions.filter(user_id__in=following_ids)
    # selected_related only works for one-to-one or foreign key relations
    # actions = actions.select_related('user', 'user__profile')[:10]
    # Therefore using prefetch_related which works for all kind of relations
    actions = actions.select_related('user', 'user__profile').prefetch_related('target')
    paginator = Paginator(actions, 2)
    page = request.GET.get('page')
    try:
        actions = paginator.page(page)
    except PageNotAnInteger:
        #  If the page is not Integer, deliver the first page
        actions = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            # if the request is AJAX and page is out of range
            # return an empty page
            return HttpResponse('')
        actions = paginator.page(paginator.num_pages)
    return render(request, 'account/dashboard.html', {'section': 'dashboard',
                                                      'actions': actions})


def register(request):

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Create User object but avoid saving it
            new_user = form.save(commit=False)
            # Set the chosen password
            new_user.set_password(form.cleaned_data['password'])
            # Now save the User, since password is set
            new_user.save()
            # create Profile for User
            Profile.objects.create(user=new_user)
            create_action(new_user, 'Has created an account')
            return render(request, 'account/register_done.html',
                          {'new_user': new_user})
    else:
        form = UserRegistrationForm()

    return render(request, 'account/register.html', {'user_form': form})


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST,
                                       files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile Updated Successfully')
        else:
            messages.error(request, 'Failed to upload the profile')
    else:

        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    return render(request, 'account/edit.html', {'user_form': user_form,
                                                 'profile_form': profile_form})


@login_required
def user_list(request):
    """
    list all users
    """

    users = User.objects.filter(is_active=True).exclude(id=request.user.id)
    return render(request, 'account/user/list.html', {'users': users,
                                                      'section': 'people'})


@login_required
def user_details(request, username):
    """
    details of given username's user
    """

    user = get_object_or_404(User, username=username, is_active=True)
    return render(request, 'account/user/details.html', {'user': user,
                                                         'section': 'people'})


@login_required
@ajax_required
@require_POST
def user_follow(request):
    """
    follow the user
    """

    user_id = request.POST.get('id')
    action = request.POST.get('action')

    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(from_user=request.user,
                                              to_user=user)
                create_action(request.user, 'is following', user)
            else:
                Contact.objects.filter(from_user=request.user, to_user=user).delete()
                create_action(request.user, 'unfollowed', user)
            return JsonResponse({'status': 'Ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error'})

    return JsonResponse({'status': 'error'})
