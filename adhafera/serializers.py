from rest_framework import serializers
from adhafera.dbmodify import move_list_item, move_user_list
from adhafera.dbquery import get_list_item_count, get_user_list_count
from .models import Item, List, ListUser

# GET SERIALIZERS

class ItemSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)

    quantity = serializers.IntegerField(required=False) # only use for QUANT lists
    text = serializers.CharField(max_length=500)
    sequence_position = serializers.IntegerField()
    checked = serializers.BooleanField(default=False)


    def create(self, validated_data):
        item = Item(**validated_data)

        print(validated_data)

        # valid sequence_position values depend on other records in the database so we'll check on that here
        if item.sequence_position < 1:
            raise serializers.ValidationError('item position may not be lower than 1')
        list_item_count = get_list_item_count(item.list_id) # could use item.list_id too
        end_position = list_item_count + 1
        if item.sequence_position > end_position:
            raise serializers.ValidationError('item position may not be greater than list item count +1')

        # create item (then move to target position if other than end of list)
        if item.sequence_position == end_position:
            item.save()
        else:
            target_position = item.sequence_position
            item.sequence_position = end_position # create item at end of list
            item.save()
            move_list_item(item, target_position) # move_list_item updates sequence_position to target_position

        return item

    def update(self, instance: Item, validated_data):
        new_quantity = validated_data.get('quantity')
        new_text = validated_data.get('text')
        new_position = validated_data.get('sequence_position')
        new_checked_value = validated_data.get('checked')

        if new_quantity is not None and new_quantity:
            instance.quantity = new_quantity
        if new_text is not None:
            instance.text = new_text
        if new_checked_value is not None:
            instance.checked = new_checked_value
        instance.save()

        if new_position is not None and new_position != instance.sequence_position:
            # valid sequence_position values depend on other records in the database so we'll check on that here
            if new_position < 1:
                raise serializers.ValidationError('item position may not be lower than 1')
            list_item_count = get_list_item_count(self. list_id)
            if new_position > list_item_count:
                raise serializers.ValidationError('new position may not be greater than the largest position in the list')
            move_list_item(instance, new_position) # move_list_item updates sequence_position to target_position

        return instance


# ItemUpdateSerializer is identical to ItemSerializer besides making the required fields optional
class ItemUpdateSerializer(ItemSerializer):
    text = serializers.CharField(max_length=500, required=False)
    sequence_position = serializers.IntegerField(required=False)
    checked = serializers.BooleanField(default=False, required=False)


class ListSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)

    title = serializers.CharField(max_length=100)
    list_type = serializers.ChoiceField(choices=List.LIST_TYPE_CHOICES)
    created_at = serializers.DateField(read_only=True)

    # this generates a query per list - would be better to leverage the ORM and a single query
    list_position = serializers.SerializerMethodField('get_list_position')
    def get_list_position(self, list: List):
        user_id = self.context.get('user_id')
        list_id = list.id
        if user_id is None:
            raise serializers.ValidationError('serializer failed to extract user id from context')
        userlistinfo = ListUser.objects.all().filter(user_id=user_id).filter(list_id=list_id).first()
        if userlistinfo is None:
            raise serializers.ValidationError('serializer failed to find user list info')
        return userlistinfo.list_position

    items = ItemSerializer(many=True, read_only=True) # maybe we can allow this to be optionally populated (instantiate lists with items)
    listusers = serializers.SlugRelatedField(
            many=True,
            read_only=True,
            slug_field='user__username'
    )

    def create(self, validated_data):
        user_id = self.context.get('user_id')
        if user_id is None:
            raise serializers.ValidationError('serializer failed to extract user id from context')

        incoming_list_position = validated_data.pop('list_position', None)

        list = List(**validated_data)
        list.save()

        # determine target list_position
        user_list_count = get_user_list_count(user_id)
        end_position = user_list_count + 1
        if incoming_list_position is not None:
            if incoming_list_position < 1:
                raise serializers.ValidationError('user list position may not be lower than 1')
            if incoming_list_position > end_position:
                raise serializers.ValidationError('user list position may not be greater than user list count +1')

        # associate creator with list
        listuser = ListUser()
        listuser.user_id = user_id
        listuser.list_id = list.id
        listuser.list_position = end_position

        print(listuser.user_id)
        print(listuser.list_id)
        print(listuser.list_position)

        listuser.save()
        if incoming_list_position is not None and incoming_list_position != end_position:
            move_user_list(listuser, incoming_list_position)

        return list

    def update(self, instance: List, validated_data):
        user_id = self.context.get('user_id')
        if user_id is None:
            raise serializers.ValidationError('serializer failed to extract user id from context')

        new_title = validated_data.get('title')
        new_type = validated_data.get('list_type')
        new_position = validated_data.get('list_position')
        if new_title is not None:
            instance.title = new_title
        if new_type is not None:
            instance.list_type = new_type
        instance.save()

        # position is tracked per user (stored in listuser)
        if new_position is not None:
            listuser = ListUser.objects.filter(user_id=user_id, list_id=instance.id).first()
            if listuser is None:
                raise serializers.ValidationError('while attempting to update list_position, failed to find listuser')
            if new_position != listuser.list_position:
                if new_position < 1:
                    raise serializers.ValidationError('user list position may not be lower than 1')
                user_list_count = get_user_list_count(user_id)
                if new_position > user_list_count:
                    raise serializers.ValidationError('user list position may not be greater than user list count')
                move_user_list(listuser, new_position)

        return instance


# ListUpdateSerializer is identical to ListSerializer besides making making the required fields optional
class ListUpdateSerializer(ListSerializer):
    title = serializers.CharField(max_length=100, required=False)
    list_type = serializers.ChoiceField(choices=List.LIST_TYPE_CHOICES, required=False)


class ShareCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)
