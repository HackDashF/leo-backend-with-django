from django.db.transaction import atomic
# from django.http import HttpResponse
# from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from adhafera.dbmodify import clear_expired_share_codes, delete_list_item, delete_list_user

from .dbquery import check_user_has_access_to_list, get_user_list_count
from .models import List, Item, ListShareCode, ListUser
from .serializers import ItemUpdateSerializer, ListSerializer, ItemSerializer, ListUpdateSerializer, ShareCodeSerializer
import logging


# NOTE: login is required for all endpoints (configured in settings)
#   but we'll check it anyway since we use request.user.id
#   in case the setting is off for development or something
#
# NOTE: adhafera is meant to provide multi-user lists
#   however, with this implementation, we'll stick with a REST server
#   ... clients shall be responsible for syncing with server to detect foreign changes
#   ... the server will act as the source of truth for list state
#   ... server will assume changes from client are fully informed of current state
#   ... server will enforce valid list state (sequential item positions for example)

logger = logging.getLogger(__name__)


@api_view(['GET', 'POST'])
@atomic
def lists(request):
    if request.user.is_authenticated is False:
        return Response({'error': 'Must be logged in to save a list'}, status=status.HTTP_401_UNAUTHORIZED)
    user_id = request.user.id

    logger.info('lists endpoint called')

    # given a GET request, return the user's lists
    if request.method == 'GET':
        queryset = List.objects.prefetch_related('items', 'listusers__user').all().filter(listusers__user_id=user_id).order_by('listusers__list_position')
        serializer = ListSerializer(queryset, many=True, context={'user_id': user_id})
        return Response(serializer.data)

    # given a POST request...
    elif request.method == 'POST':
        # create new list
        new_list_serializer = ListSerializer(data=request.data, context={'user_id': user_id})
        new_list_serializer.is_valid(raise_exception=True)
        new_list_serializer.save()

        return Response(new_list_serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PATCH', 'DELETE'])
@atomic
def list(request, list_id):
    if request.user.is_authenticated is False:
        return Response({'error': 'Must be logged in to save a list'}, status=status.HTTP_401_UNAUTHORIZED)
    user_id = request.user.id
    if check_user_has_access_to_list(user_id, list_id) is False:
        Response({'error': 'the list does not exist or access is deined'})

    listuser = get_object_or_404(ListUser, list_id=list_id, user_id=user_id)
    list = listuser.list

    if request.method == 'GET':
        serializer = ListSerializer(list, context={'user_id': user_id})
        return Response(serializer.data)
    elif request.method == 'PATCH':
        serializer = ListUpdateSerializer(list, data=request.data, context={'user_id': user_id})
        serializer.is_valid(raise_exception=True)
        serializer.save() # user_id is required from context
        return Response(serializer.data)
    elif request.method == 'DELETE':
        delete_list_user(listuser)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def items(request, list_id):
    if request.user.is_authenticated is False:
        return Response({'error': 'Must be logged in to save a list'}, status=status.HTTP_401_UNAUTHORIZED)
    user_id = request.user.id
    if check_user_has_access_to_list(user_id, list_id) is False:
        Response({'error': 'the list does not exist or access is deined'})

    serializer = ItemSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(list_id=list_id)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['PATCH', 'DELETE'])
def item(request, list_id, item_id):
    if request.user.is_authenticated is False:
        return Response({'error': 'Must be logged in to save a list'}, status=status.HTTP_401_UNAUTHORIZED)
    user_id = request.user.id
    if check_user_has_access_to_list(user_id, list_id) is False:
        Response({'error': 'the list does not exist or access is deined'})

    item = get_object_or_404(Item, pk=item_id)

    if request.method == 'PATCH':
        serializer = ItemUpdateSerializer(item, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == 'DELETE':
        delete_list_item(item)
        return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        return Response({"error": "Only PATCH and DELETE method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
def share(request, list_id):
    if request.user.is_authenticated is False:
        return Response({'error': 'Must be logged in to save a list'}, status=status.HTTP_401_UNAUTHORIZED)
    user_id = request.user.id
    if check_user_has_access_to_list(user_id, list_id) is False:
        Response({'error': 'the list does not exist or access is deined'})

    username = request.data.get('username')
    if username is None:
        Response({'error': 'you must specify the username to create a share code for'})

    clear_expired_share_codes()

    # first check for existing, non-expired share code for this list and user
    share_code = ListShareCode.objects.all().filter(list_id=list_id).filter(username=username).first()

    # else create one
    if share_code is None:
        code = get_random_string(length=6)

        share_code = ListShareCode()
        share_code.list_id = list_id
        share_code.username = username
        share_code.code = code
        share_code.save()

    code_serializer = ShareCodeSerializer(share_code)

    return Response(code_serializer.data)


@api_view(['POST'])
def join(request):
    if request.user.is_authenticated is False:
        return Response({'error': 'Must be logged in to join a list'}, status=status.HTTP_401_UNAUTHORIZED)
    user_id = request.user.id
    username = request.user.username

    code = request.data.get('code')
    if code is None:
        Response({'error': 'no code specified'})

    clear_expired_share_codes()

    share_record = ListShareCode.objects.filter(code=code).filter(username=username).first()
    print(share_record)
    if share_record is None:
        return Response({"error": "List doesn't exist or code is invalid"})
    list_id = share_record.list_id

    user_list_count = get_user_list_count(user_id)
    list_position = user_list_count + 1
    if isinstance(user_list_count, str):
        return Response({'error': 'Failed to enumerate user\'s other lists'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    list_user = ListUser()
    list_user.list_id = list_id
    list_user.user_id = user_id
    list_user.list_position = list_position
    list_user.save()

    list = List.objects.filter(id=list_id).first()
    list_serializer = ListSerializer(list, context={'user_id': user_id})

    return Response(list_serializer.data)
