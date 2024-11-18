import csv
import re
from io import TextIOWrapper

from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import DatabaseError
from django.views.decorators.csrf import requires_csrf_token

from lists.forms import ItemForm, EditItemForm, ImportForm
from lists.models import List, Item
import logging

logger = logging.getLogger(__name__)


@login_required(login_url='/')
def index(request):
    user_lists = List.objects.filter(user=request.user)
    context = {'user_lists': user_lists}

    if user_lists.exists():
        # Retrieve or set default values
        selected_list_id = request.GET.get('list_id') or user_lists.first().id
        sort_by = 'created_at' if not request.GET.get('sort_by') or request.GET.get('sort_by') == 'date' else 'name'
        sort_order = '-' if request.GET.get('order') == 'desc' else ''

        #  Get selected list and items with applied sorting
        selected_list = get_object_or_404(List, id=selected_list_id, user=request.user)
        selected_list_items = Item.objects.filter(list__id=selected_list_id).order_by(sort_order + sort_by)

        # TODO: Improve sorting for template
        # Sorting options for the template
        sort_fields = {'date': 'Date', 'name': 'Name'}
        sort_directions = {'asc': 'Asc', 'desc': 'Desc'}

        context.update({
            'selected_list': selected_list,
            'list_items': selected_list_items,
            'add_item_form': ItemForm(initial={'list': selected_list}),
            'edit_item_form': EditItemForm(),
            'sort_fields': sort_fields,
            'sort_directions': sort_directions,
            'import_form': ImportForm(),
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
        messages.success(request, 'List "%s" has been created' % list_name)
        return redirect('/lists/?list_id=%s' % new_list.id)
    except DatabaseError as e:
        logger.warning(f"Failed to create list '{list_name}': {e}")
        messages.error(request, 'An error occurred while adding the list.')
        return redirect('/lists')


@login_required(login_url='/')
def delete_list(request, list_id):
    list_to_delete = get_object_or_404(List, id=list_id, user=request.user)
    try:
        list_to_delete.delete()
        messages.success(request, 'List "%s" has been deleted' % list_id)
    except DatabaseError as e:
        logger.warning(f"Failed to delete list '{list_id}': {e}")
        messages.error(request, 'An error occurred while deleting the list.')
    return redirect('/lists/')


@login_required(login_url='/')
@requires_csrf_token
def add_item(request, list_id):
    selected_list = get_object_or_404(List, id=list_id, user=request.user)
    if request.method == 'POST':
        add_item_form = ItemForm(request.POST)
        if add_item_form.is_valid():
            try:
                new_item = add_item_form.save()
                messages.success(request, 'Item "%s" has been added to list "%s"' % (new_item, selected_list.name))
            except DatabaseError as e:
                logger.warning(f"Failed to add item for list '{list_id}': {e}")
                messages.error(request, 'An error occurred while adding item to the list.')
    return redirect('/lists/?list_id=%s' % list_id)


@login_required(login_url='/')
def delete_item(request, item_id):
    item_to_delete = get_object_or_404(Item, id=item_id)
    try:
        item_to_delete.delete()
        messages.success(request, 'Item "%s" has been deleted' % item_to_delete.name)
    except DatabaseError as e:
        logger.warning(f"Failed to delete item {item_id}: {e}")
        messages.error(request, 'An error occurred while deleting the item.')
    return redirect('/lists/?list_id=%s' % item_to_delete.list.id)


@login_required(login_url='/')
@requires_csrf_token
def edit_item(request, item_id):
    # TODO: Improve this flow
    item_to_edit = get_object_or_404(Item, id=item_id)
    try:
        if request.method == 'POST':
            edit_item_form = EditItemForm(request.POST, instance=item_to_edit)
            if edit_item_form.is_valid():
                edit_item_form.save()
        messages.success(request, 'Item "%s" has been edited' % item_to_edit.name)
    except DatabaseError as e:
        logger.warning(f"Failed to edit item {item_id}: {e}")
        messages.error(request, 'An error occurred while editing the item.')
    return redirect('/lists/?list_id=%s' % item_to_edit.list.id)


@login_required(login_url='/')
def mark_item_complete(request, item_id):
    marked_item = get_object_or_404(Item, id=item_id)
    marked_item.is_completed = True
    try:
        marked_item.save()
        messages.success(request, 'Item "%s" has been marked as complete' % marked_item.name)
    except DatabaseError as e:
        logger.warning(f"Failed to mark item complete {item_id}: {e}")
        messages.error(request, 'An error occurred while marking the item complete.')
    return redirect('/lists/?list_id=%s' % marked_item.list.id)


@login_required(login_url='/')
def get_item_data(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    return JsonResponse({'name': item.name, 'color': item.color})


@login_required(login_url='/')
@requires_csrf_token
def import_list(request):
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            import_option = form.cleaned_data['option']
            try:
                with TextIOWrapper(request.FILES['file'], encoding=request.encoding) as import_file:
                    csv_reader = csv.DictReader(import_file, delimiter=',')
                    lists_id_mapping = {}
                    # TODO: Validate csv file headers
                    for row_number, row in enumerate(csv_reader, start=1):
                        error_messages = []
                        # Validate item data
                        if not row['ItemName']:
                            error_messages.append('Item name is empty!')
                        if row['Color'] and not re.fullmatch(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', row['Color']):
                            error_messages.append('Color code is invalid!')
                        if row['IsCompleted'] not in ['True', 'False', '']:
                            error_messages.append('Is Completed value is invalid!')

                        # Validate list data based on selected import option
                        # If all are new lists & items
                        if import_option == 'new-lists':
                            if not row['ListName']:
                                error_messages.append('List name is empty!')
                            if not row['ListId']:
                                error_messages.append('List ID is empty!')
                        # If only items are to be imported, list ID should be provided
                        elif import_option == 'items-only':
                            if not row['ListId']:
                                error_messages.append('List ID is empty!')
                            elif not List.objects.filter(id=row['ListId']).exists():
                                error_messages.append('List "%s" does not exist!' % row['ListId'])
                        # If existing lists' IDs are provided along with new lists
                        elif import_option == 'existing-lists':
                            if not row['ListId'] and not row['ListName']:
                                error_messages.append('List Name or ID is should be provided!')
                            if row['ListId'] and not List.objects.filter(id=row['ListId']).exists():
                                error_messages.append('List "%s" does not exist!' % row['ListId'])

                        if len(error_messages) > 0:
                            # TODO: If too many errors, show only row numbers
                            messages.error(
                                request,
                                f"Error in adding data for row {row_number}: {', '.join(error_messages)}",
                            )
                            continue

                        # Create item
                        new_item = Item(
                            name=row['ItemName'],
                            is_completed=row['IsCompleted'] == 'True',
                        )
                        if row['Color']:
                            new_item.color = row['Color']

                        if import_option == 'items-only':
                            new_item.list_id = row['ListId']
                        elif import_option == 'existing-lists' and row['ListId']:
                            new_item.list_id = row['ListId']
                        else:
                            # Check if the list is already created, else create list
                            if not lists_id_mapping.get(row['ListId']):
                                new_list = List(name=row['ListName'], user=request.user)
                                new_list.save()
                                lists_id_mapping[row['ListId']] = new_list.id
                            new_item.list_id = lists_id_mapping[row['ListId']]

                        new_item.save()
                messages.success(request, '%s imported.' % request.FILES['file'].name)

            except Exception as e:
                logger.error('Error in importing file %s\n%s', request.FILES['file'].name, e, exc_info=True)
                messages.error(request, 'Import failed.')
    return redirect('/lists/')
