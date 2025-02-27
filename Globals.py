GLOBAL_FONT_SIZE = 14
GLOBAL_SMALL_FONT_SIZE = 10
GLOBAL_ENEMY_FONT_SIZE = 18
GLOBAL_OVERLAY_FONT_SIZE = 30


def set_global_font_size(new_font_size):
    global GLOBAL_FONT_SIZE
    GLOBAL_FONT_SIZE = new_font_size


def set_global_small_font_size(new_font_size):
    global GLOBAL_SMALL_FONT_SIZE
    GLOBAL_SMALL_FONT_SIZE = new_font_size


def set_global_enemy_font_size(new_font_size):
    global GLOBAL_ENEMY_FONT_SIZE
    GLOBAL_ENEMY_FONT_SIZE = new_font_size


def set_global_overlay_font_size(new_font_size):
    global GLOBAL_OVERLAY_FONT_SIZE
    GLOBAL_OVERLAY_FONT_SIZE = new_font_size


def get_global_font_size():
    return GLOBAL_FONT_SIZE


def get_global_small_font_size():
    return GLOBAL_SMALL_FONT_SIZE


def get_global_enemy_font_size():
    return GLOBAL_ENEMY_FONT_SIZE


def get_global_overlay_font_size():
    return GLOBAL_OVERLAY_FONT_SIZE
