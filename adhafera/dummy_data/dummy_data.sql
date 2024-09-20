-- dummy data for testing list app 'adhafera'
-- this dummy data requires two users be created with usernames 'ron' and 'sue'

INSERT INTO leo.adhafera_list (id, title, list_type) values (1, 'Ron Todo', 'BASIC');
INSERT INTO leo.adhafera_list (id, title, list_type) values (2, 'Sue Todo', 'BASIC');
INSERT INTO leo.adhafera_list (id, title, list_type) values (3, 'Shopping', 'QUANT');

INSERT INTO leo.adhafera_item (`id`, `list_id`, `quantity`, `text`, `sequence_position`, `checked`) VALUES (1, 1, NULL, 'Do Prayers', 1, 1);
INSERT INTO leo.adhafera_item (`id`, `list_id`, `quantity`, `text`, `sequence_position`, `checked`) VALUES (2, 1, NULL, 'Eat Breakfast', 2, 0);
INSERT INTO leo.adhafera_item (`id`, `list_id`, `quantity`, `text`, `sequence_position`, `checked`) VALUES (3, 1, NULL, 'Feed Dogs', 3, 0);
INSERT INTO leo.adhafera_item (`id`, `list_id`, `quantity`, `text`, `sequence_position`, `checked`) VALUES (4, 2, NULL, 'Pray', 1, 1);
INSERT INTO leo.adhafera_item (`id`, `list_id`, `quantity`, `text`, `sequence_position`, `checked`) VALUES (5, 2, NULL, 'Eat', 2, 0);
INSERT INTO leo.adhafera_item (`id`, `list_id`, `quantity`, `text`, `sequence_position`, `checked`) VALUES (6, 2, NULL, 'Garden', 3, 0);
INSERT INTO leo.adhafera_item (`id`, `list_id`, `quantity`, `text`, `sequence_position`, `checked`) VALUES (7, 3, 2, 'Dozen Eggs', 1, 0);
INSERT INTO leo.adhafera_item (`id`, `list_id`, `quantity`, `text`, `sequence_position`, `checked`) VALUES (8, 3, 1, 'Yogurt', 2, 0);

-- (`id`, `list_order`, `list_id`, `user_id`)
INSERT INTO leo.adhafera_listuser SELECT 1, 1, 1, id FROM leo.users_user WHERE `username` = 'ron';
INSERT INTO leo.adhafera_listuser SELECT 2, 2, 2, id FROM leo.users_user WHERE `username` = 'sue';
INSERT INTO leo.adhafera_listuser SELECT 3, 2, 3, id FROM leo.users_user WHERE `username` = 'ron';
INSERT INTO leo.adhafera_listuser SELECT 4, 1, 3, id FROM leo.users_user WHERE `username` = 'sue';

INSERT INTO leo.adhafera_listsharecode (`id`, `list_id`, `code`) VALUES (1, 3, 'CODE4U');
