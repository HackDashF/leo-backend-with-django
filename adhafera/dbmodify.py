from django.db import connections
from django.db.backends.utils import CursorWrapper
from django.shortcuts import get_object_or_404

from adhafera.dbquery import count_list_users, get_user_lists_sequence_min_max_and_count, get_list_items_sequence_min_max_and_count
from adhafera.models import Item, List, ListUser

# -------------------------------------------------- POSITION REQUIREMENTS
#
# position values for USER LISTs & LIST ITEMs shall:
# - start at 1
# - be sequential
#
# -------------------------------------------------- RE-ORDERING
#
# because position changes affect more than one record,
# position changes will be handled as a separate concern, here
# although this will cause some extra database queries, it simplifies code
#
# -------------------------------------------------- RE-ORDERING STEPS
#
# - move target record to position 0 (reserved for this process)
# - shuffle records between original position and target position up (or down)
# - move target record to, now open, target position
#
# -------------------------------------------------- EXAMPLES
# symbol + is target record
# symbol # are other records in sequence
#
# Example: Move item from position 3 to 6
#      0 1 2 3 4 5 6 7 8   | position columns
#        # # + # # # # #   |
#      + # #   # # # # #   | STEP1 - move target item to position 0
#      + # # # # #   # #   | STEP2 - decrement items 3-6 (note: position 3 is vacant so no conflict at 2)
#        # # # # # + # #   | STEP3 - update target item to position 6
#
# Example: Move item from position 6 to 3
#      0 1 2 3 4 5 6 7 8   | position columns
#        # # # # # + # #   |
#      + # # # # #   # #   | STEP1 - move target item to position 0
#      + # #   # # # # #   | STEP2 - increment items 3-6 (note: position 6 is vacant so there will be no conflict at 7)
#        # # + # # # # #   | STEP3 - update target item to position 3
#

# -------------------------------------------------- LIST SHARE CODES

def clear_expired_share_codes():
    with connections['default'].cursor() as cursor:
        # delete any share codes older than 10 minutes
        VALID_FOR = '0:10:0'
        cursor.execute(
            "DELETE FROM leo.adhafera_listsharecode WHERE UTC_TIMESTAMP() > ADDTIME(created_at, %s)",
            [VALID_FOR]
        )


# -------------------------------------------------- USER LISTS

def move_user_list(listuser:ListUser, new_position:int):
    with connections['default'].cursor() as cursor:

        old_position = listuser.list_position

        __set_user_list_to_position(cursor, listuser.id, 0)

        # shuffle items up or down between original and target positions
        if old_position < new_position:
            __decrement_user_list_positions_between(cursor, listuser.user_id, old_position, new_position)
        else:
            __increment_user_list_positions_between(cursor, listuser.user_id, new_position, old_position)

        __set_user_list_to_position(cursor, listuser.id, new_position)

        # ensure ending item sequence values in the database are valid - exception raised if not
        minMaxCount = get_user_lists_sequence_min_max_and_count(cursor, listuser.user_id)
        if minMaxCount[0] is not None:
            __check_sequence_integrity(*minMaxCount)

        # if everything looks good, update the sequence position of the argument item
        listuser.list_position = new_position


def delete_list_user(listuser:ListUser):
    with connections['default'].cursor() as cursor:

        list_id = listuser.list_id
        user_id = listuser.user_id
        deleted_list_position = listuser.list_position

        list = listuser.list

        # delete ListUser (delete for user)
        listuser.delete()

        # if no users remain for this list, delete the list itself also
        if count_list_users(list_id) == 0:
            list.delete()

        __decrement_user_list_positions_above(cursor, user_id, deleted_list_position)

        # ensure ending item sequence values in the database are valid - exception raised if not
        minMaxCount = get_user_lists_sequence_min_max_and_count(cursor, user_id)
        if minMaxCount[0] is not None:
            __check_sequence_integrity(*minMaxCount)


def __set_user_list_to_position(cursor:CursorWrapper, listuser_id:int, position:int):
    cursor.execute(
        "UPDATE leo.adhafera_listuser SET list_position = %s WHERE id = %s",
        [position, listuser_id])


def __decrement_user_list_positions_above(cursor:CursorWrapper, user_id:int, position:int):
    cursor.execute(
        "UPDATE leo.adhafera_listuser SET list_position = list_position - 1" +
        " WHERE user_id = %s AND list_position > %s",
        [user_id, position])


def __decrement_user_list_positions_between(cursor:CursorWrapper, user_id:int, start_position_inclusive:int, end_position_inclusive:int):
    cursor.execute(
        "UPDATE leo.adhafera_listuser SET list_position = list_position - 1" +
        " WHERE user_id = %s AND list_position >= %s AND list_position <= %s",
        [user_id, start_position_inclusive, end_position_inclusive])


def __increment_user_list_positions_between(cursor:CursorWrapper, user_id:int, start_position_inclusive:int, end_position_inclusive:int):
    cursor.execute(
        "UPDATE leo.adhafera_listuser SET list_position = list_position + 1" +
        " WHERE user_id = %s AND list_position >= %s AND list_position <= %s",
        [user_id, start_position_inclusive, end_position_inclusive])


# -------------------------------------------------- LIST ITEMS

def move_list_item(item:Item, new_position:int):
    with connections['default'].cursor() as cursor:

        old_position = item.sequence_position

        __set_item_to_position(cursor, item.id, 0)

        # shuffle items up or down between original and target positions
        if old_position < new_position:
            __decrement_list_item_positions_between(cursor, item.list_id, old_position, new_position)
        else:
            __increment_list_item_positions_between(cursor, item.list_id, new_position, old_position)

        __set_item_to_position(cursor, item.id, new_position)

        # ensure ending item sequence values in the database are valid - exception raised if not
        minMaxCount = get_list_items_sequence_min_max_and_count(cursor, item.list_id)
        if minMaxCount[0] is not None:
            __check_sequence_integrity(*minMaxCount)

        # if everything looks good, update the sequence position of the argument item
        item.sequence_position = new_position


def delete_list_item(item:Item):
    with connections['default'].cursor() as cursor:

        list_id = item.list_id
        deleted_item_position = item.sequence_position

        item.delete()

        __decrement_list_item_positions_above(cursor, list_id, deleted_item_position)

        # ensure ending item sequence values in the database are valid - exception raised if not
        minMaxCount = get_list_items_sequence_min_max_and_count(cursor, item.list_id)
        if minMaxCount[0] is not None:
            __check_sequence_integrity(*minMaxCount)


def __set_item_to_position(cursor:CursorWrapper, item_id:int, position:int):
    cursor.execute(
        "UPDATE leo.adhafera_item SET sequence_position = %s WHERE id = %s",
        [position, item_id])


def __decrement_list_item_positions_above(cursor:CursorWrapper, list_id:int, position:int):
    cursor.execute(
        "UPDATE leo.adhafera_item SET sequence_position = sequence_position - 1" +
        " WHERE list_id = %s AND sequence_position > %s",
        [list_id, position])


def __decrement_list_item_positions_between(cursor:CursorWrapper, list_id:int, start_position_inclusive:int, end_position_inclusive:int):
    cursor.execute(
        "UPDATE leo.adhafera_item SET sequence_position = sequence_position - 1" +
        " WHERE list_id = %s AND sequence_position >= %s AND sequence_position <= %s",
        [list_id, start_position_inclusive, end_position_inclusive])


def __increment_list_item_positions_between(cursor:CursorWrapper, list_id:int, start_position_inclusive:int, end_position_inclusive:int):
    cursor.execute(
        "UPDATE leo.adhafera_item SET sequence_position = sequence_position + 1" +
        " WHERE list_id = %s AND sequence_position >= %s AND sequence_position <= %s",
        [list_id, start_position_inclusive, end_position_inclusive])


# -------------------------------------------------- SEQUENCE INTEGRITY

# User's list ordering and List's item ordering should be sequential starting at 1
# - minimum must always be 1
# - the database prevents duplicate position values with unique keys
# - maximum must be equal to the count (assures a sequence with no gaps)
def __check_sequence_integrity(min:int, max:int, count:int):
    if max != count:
        raise Exception('max {} not equal to count {}'.format(max, count))

    if min != 1:
        raise Exception('min {} not equal to one'.format(min))
