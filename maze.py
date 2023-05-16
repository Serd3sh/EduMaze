import config
from renderProxy import *
from typing import Optional, NewType
from random import randint

MazeField = NewType("MazeField", dict[Vector2, list[int, bool, int, Optional[Texture]]])
"""
Позиция(Vector2): [ Тип_клетки(int), туман(bool), рандом_число(int), текстура(render.Texture) ]
"""

# типы клеток в лабиринте
EMPTY = 0  # Еще не занята. Используется в процессе генерации
WALL = 1   # Стена. В процессе генерации возможна перезапись
ROAD = 2   # Дорога. В процессе генерации неизменна

CELL_ID = 0
CELL_FOG = 1
CELL_RAND = 2
CELL_OBJ = 3

# массив с направлениями для удобного циклического выбора
DIRECTIONS = [
    Vector2(-2, 0), Vector2(0, -2),
    Vector2(2, 0), Vector2(0, 2)
]


def GetDirections(field: MazeField, pos, neighborId, farNeighbor=True):
    """
    Определить возможные направления относительно указанной клетки
    :param field: Пола лабиринта, в котором необходим поиск
    :param Vector2 pos: Позиция, относительно которой должен идти поиск
    :param int neighborId: ID необходимого соседа
    :param bool farNeighbor: True, если искать на 2 клетки вперед, иначе на 1
    :returns: Массив с доступными соседями
    """
    res = []
    n = 1 if farNeighbor else 2
    for i in range(0, 4):
        neighbor = pos + DIRECTIONS[i] / n
        if 0 <= neighbor.x < config.MAZE_SIZE.x and 0 <= neighbor.y < config.MAZE_SIZE.y and \
                field[neighbor][CELL_ID] == neighborId:
            res.append(DIRECTIONS[i] / n)
    return res


def GenerateMaze(field_size) -> MazeField:
    """
    Генератор лабиринта
    :param Vector2 field_size: Размер создаваемого лабиринта(должен быть нечетным по двум осям)
    :returns: Массив с созданным лабиринтом
    """
    field: MazeField = MazeField({})
    incomplete_roads = []

    # создаем пустую сетку, от которой будет идти генерация
    for y in range(0, int(field_size.y)):
        for x in range(0, int(field_size.x)):
            pos = Vector2(x, y)
            if x == 0 and y == 0:
                field[pos] = [ROAD, config.FOG_ENABLED, randint(0, 99), None]
                incomplete_roads.append(pos)
            elif x % 2 == 0 and y % 2 == 0:
                field[pos] = [EMPTY, config.FOG_ENABLED, randint(0, 99), None]
            else:
                field[pos] = [WALL, config.FOG_ENABLED, randint(0, 99), None]

    # путем змеек создаем пути. Если змейка врезалась и не может никуда свернуть -
    # - возвращаемся туда, где проложили дорогу, и продолжаем создавать путь(тут будет развилка)
    pos = None
    while True:
        # определяем есть ли смысл вести змейку
        while True:
            if len(incomplete_roads) == 0:
                break
            pos = incomplete_roads[randint(0, len(incomplete_roads) - 1)] if pos is None else pos
            can_move = False

            # определяем можем ли мы вообще от сюда продолжить змейку
            for i in range(0, 4):
                near_pos = pos + DIRECTIONS[i]
                if field_size.x > near_pos.x >= 0 and field_size.y > near_pos.y >= 0 \
                        and field[near_pos][CELL_ID] == EMPTY:
                    can_move = True
                    break

            # случай, если позиция изменена. То есть, взята не из массива incomplete_roads
            # здесь проверяем помечена ли эта клетка как клетка, от которой можно провести змейку
            found = False
            for i in range(0, len(incomplete_roads)):
                if incomplete_roads[i] == pos:
                    found = True
                    break

            # условия по порядку:
            # двигаться нельзя, эта клетка есть в массиве = неактуально, убираем из массива
            # двигаться можно, но клетки в массиве нет = добавляем в массив. Возможно вернемся сюда
            # двигаться нельзя, клетки в массиве нет = сбрасываем позиция и ищем новую клетку для продолжения
            # двигаться можно, клетка в массиве = все ок, выходим и долбим проход
            if not can_move and found:
                incomplete_roads.remove(pos)
            elif can_move and not found:
                incomplete_roads.append(pos)
            elif not can_move and not found:
                pos = None
                continue
            else:
                break

        # перестраховка - возможно лабиринт уже создан
        # цикл выше гарантирует, что если массив пустой, то лабирнит создан
        if len(incomplete_roads) == 0:
            break

        # а тут прокладываем путь
        dirs = GetDirections(field, pos, EMPTY)

        cur_dir = dirs[randint(0, len(dirs) - 1)]
        field[pos + cur_dir][CELL_ID] = ROAD
        field[pos + cur_dir / 2][CELL_ID] = ROAD
        pos = pos + cur_dir

    return field
