from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from images.forms import ImageCreateForm
from images.models import Image
from common.decorators import ajax_required
from django.http import HttpResponse
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from actions.utils import create_action, get_redis
from libs.constants import KEY_IMAGE_RANKING
import pdb

redis = get_redis()


@login_required
def image_create(request):
    if request.method == 'POST':
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_item = form.save(commit=False)
            new_item.user = request.user
            new_item.save()
            create_action(request.user, 'Bookmarked an image', new_item)

            messages.success(request, 'Image added Successfully')

            # redirect to new created item details view
            return redirect(new_item.get_absolute_url())
    else:
        form = ImageCreateForm(data=request.GET)

    return render(request, 'images/image/create.html', {
        'section': 'images', 'form': form
    })


def image_details(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    total_view = redis.incr(f'image:{image.id}:views')
    redis.zincrby(KEY_IMAGE_RANKING, 1, image.id)

    return render(request, 'images/image/details.html',
                  {'section': 'images', 'image': image,
                   'total_view': total_view})


@ajax_required
@login_required
@require_POST
def image_like(request):
    image_id = request.POST['id']
    action = request.POST['action']
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, action, image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'Ok'})
        except Exception as _:
            pass

    return JsonResponse({'status': 'Error'})


@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        #  If the page is not Integer, deliver the first page
        images = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            # if the request is AJAX and page is out of range
            # return an empty page
            return HttpResponse('')
        images = paginator.page(paginator.num_pages)

    if request.is_ajax():
        return render(request, 'images/image/list_ajax.html',
                      {'section': 'images', 'images': images})

    return render(request, 'images/image/list.html',
                  {'section': 'images', 'images': images})


@login_required
def image_ranking(request):
    # get images ranking dict
    image_dic = redis.zrange(KEY_IMAGE_RANKING, 0, -1, desc=True)
    image_ids_by_ranking = [int(img_id) for img_id in image_dic]
    most_viewed_images = list(Image.objects.filter(id__in=image_ids_by_ranking))
    most_viewed_images.sort(key=lambda x: image_ids_by_ranking.index(x.id))
    return render(request, 'images/image/ranking.html', {
        'section': 'images', 'most_viewed_images': most_viewed_images
    })
