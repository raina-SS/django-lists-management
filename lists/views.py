from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import DatabaseError
from django.views.decorators.csrf import requires_csrf_token

from lists.models import List, Item
import logging

logger = logging.getLogger(__name__)


@login_required(login_url='/')
def index(request):
    user_lists = List.objects.filter(user=request.user)
    context = {'user_lists': user_lists}
    if user_lists.exists():
        selected_list_id = request.GET.get('list_id') or user_lists.first().id
        selected_list = get_object_or_404(List, id=selected_list_id, user=request.user)
        selected_list_items = Item.objects.filter(list__id=selected_list_id)
        context.update({
            'selected_list': selected_list,
            'list_items': selected_list_items,
        })
    return render(request, 'lists/index.html', context)


@login_required(login_url='/')
@requires_csrf_token
def add_list(request):
    list_name = request.POST.get('list_name')
    # TODO: How to validate model attributes
    if not list_name:
        return HttpResponseBadRequest("Name required")
    try:
        new_list = List.objects.create(name=list_name, user=request.user)
    except DatabaseError as e:
        logger.warning(f"Failed to create list '{list_name}': {e}")
        messages.error(request, 'An error occurred while adding the list.')
        return redirect('/lists')
    else:
        messages.success(request, 'List "%s" has been created' % list_name)
        return redirect('/lists/?list_id=%s' % new_list.id)


@login_required(login_url='/')
def delete_list(request, list_id):
    list_to_delete = get_object_or_404(List, id=list_id, user=request.user)
    try:
        list_to_delete.delete()
    except DatabaseError as e:
        logger.warning(f"Failed to delete list '{list_id}': {e}")
        messages.error(request, 'An error occurred while deleting the list.')
    else:
        messages.success(request, 'List "%s" has been deleted' % list_id)
    return redirect('/lists/')


@login_required(login_url='/')
@requires_csrf_token
def add_item(request, list_id):
    item_description = request.POST.get('description')
    if not item_description:
        return HttpResponseBadRequest("Description required")
    selected_list = get_object_or_404(List, id=list_id, user=request.user)
    try:
        Item.objects.create(list=selected_list, description=item_description)
    except DatabaseError as e:
        logger.warning(f"Failed to add item for list '{list_id}': {e}")
        messages.error(request, 'An error occurred while adding item to the list.')
    else:
        messages.success(request, 'Item "%s" has been added to list "%s"' % (item_description, selected_list.name))
    return redirect('/lists/?list_id=%s' % list_id)


@login_required(login_url='/')
def delete_item(request, item_id):
    item_to_delete = get_object_or_404(Item, id=item_id)
    try:
        item_to_delete.delete()
    except DatabaseError as e:
        logger.warning(f"Failed to delete item {item_id}: {e}")
        messages.error(request, 'An error occurred while deleting the item.')
    else:
        messages.success(request, 'Item "%s" has been deleted' % item_id)
    return redirect('/lists/?list_id=%s' % item_to_delete.list.id)


@login_required(login_url='/')
def mark_item_complete(request, item_id):
    marked_item = get_object_or_404(Item, id=item_id)
    marked_item.is_completed = True
    try:
        marked_item.save()
    except DatabaseError as e:
        logger.warning(f"Failed to mark item complete {item_id}: {e}")
        messages.error(request, 'An error occurred while marking the item complete.')
    else:
        messages.success(request, 'Item "%s" has been marked as complete' % item_id)
    return redirect('/lists/?list_id=%s' % marked_item.list.id)
