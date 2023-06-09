"""
Файл служит для создания лабиринта, определения направлений в нем и способа обращения к массиву с лабиринтом
"""
import config
from renderProxy import *
from typing import Optional, NewType
from random import randint

# определение нового типа, что бы IDE не жаловался на некую абстракцию поля в рендере
# например, свойство текстуры может быть None
# это невозможно, т.к. перед использованием текстуры 100% загружаются и существуют
MazeField = NewType("MazeField", dict[Vector2, list[int, bool, int, Optional[Texture]]])
"""
{  Позиция(Vector2): [ Тип_клетки(int), туман(bool), рандом_число(int), текстура(render.Texture) ]  }
"""

# типы клеток в лабиринте
CID_EMPTY = "empty"         # Еще не занята. Используется в процессе генерации
CID_WALL = "wall"           # Стена. В процессе генерации возможна перезапись
CID_ROAD = "road"           # Дорога. В процессе генерации неизменна
CID_TABLE = "table"         # Пустой стол
CID_PAPER_TABLE = "papers"  # Стол с бумагами. При приближении активирует вопрос
CID_EXIT = "exit"           # Клетка выхода

# название параметров для более читаемого обращения к свойству клетки поля
# например: field[Vector2(13,14)][CELL_ID] == ROAD
CELL_ID = 0
CELL_FOG = 1
CELL_RAND = 2
CELL_OBJ = 3

# массив с направлениями для удобного циклического выбора
DIRECTIONS = [
    Vector2(-2, 0), Vector2(0, -2),
    Vector2(2, 0), Vector2(0, 2)
]


def IsCellRoadType(id) -> bool:
    """
    Проверка типа клетки на дорогу(то есть где можно пройти)
    Это актуально, т.к. выход и столы являются проходимыми
    :param str id: Проверяемый id
    :returns: True, если этот id проходимый
    """
    return id == CID_ROAD or id == CID_TABLE or id == CID_PAPER_TABLE or id == CID_EXIT

def GetDirections(field, pos, neighborId, mazeSize, farNeighbor=True):
    """
    Определить возможные направления относительно указанной клетки
    :param MazeField field: Пола лабиринта, в котором необходим поиск
    :param Vector2 pos: Позиция, относительно которой должен идти поиск
    :param str neighborId: ID необходимого соседа
    :param bool farNeighbor: True, если искать на 2 клетки вперед, иначе на 1
    :param Vector2 mazeSize: Размер лабиринта
    :returns: Массив с доступными соседями
    """
    res = []
    n = 1 if farNeighbor else 2
    for i in range(0, 4):
        neighbor = pos + DIRECTIONS[i] / n
        if 0 <= neighbor.x < mazeSize.x and 0 <= neighbor.y < mazeSize.y:
            if (neighborId == CID_ROAD and IsCellRoadType(field[neighbor][CELL_ID])) \
                    or (neighborId != CID_ROAD and field[neighbor][CELL_ID] == neighborId):
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
                field[pos] = [CID_ROAD, config.FOG_ENABLED, randint(0, 99), None]
                incomplete_roads.append(pos)
            elif x % 2 == 0 and y % 2 == 0:
                field[pos] = [CID_EMPTY, config.FOG_ENABLED, randint(0, 99), None]
            else:
                field[pos] = [CID_WALL, config.FOG_ENABLED, randint(0, 99), None]

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
                        and field[near_pos][CELL_ID] == CID_EMPTY:
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
        # цикл выше гарантирует, что если массив пустой, то лабиринт создан
        if len(incomplete_roads) == 0:
            break

        # а тут прокладываем путь
        dirs = GetDirections(field, pos, CID_EMPTY, field_size)

        cur_dir = dirs[randint(0, len(dirs) - 1)]
        field[pos + cur_dir][CELL_ID] = CID_ROAD
        field[pos + cur_dir / 2][CELL_ID] = CID_ROAD
        pos = pos + cur_dir

    # создание столов в тупиках
    paperTableCount = 0
    tableCount = 0
    cellsWithTable = []
    for y in range(0, int(field_size.y)):
        for x in range(0, int(field_size.x)):
            if x == 0 and y == 0:
                continue
            cell = field[Vector2(x, y)]
            if cell[CELL_ID] == CID_ROAD and len(GetDirections(field, Vector2(x, y), CID_ROAD, field_size, False)) == 1:
                tableCount += 1
                if paperTableCount <= config.MIN_PAPER_TABLES+1 or randint(1, 100) <= config.PAPER_TABLE_CHANCE:
                    cell[CELL_ID] = CID_PAPER_TABLE
                    paperTableCount += 1
                else:
                    cell[CELL_ID] = CID_TABLE
                cellsWithTable.append(Vector2(x, y))

    print(f"Interactive tables: {paperTableCount-1}/{tableCount}({int((paperTableCount-1)/tableCount*100)}%)")
    # внешние границы лабиринта
    for x in range(-1, int(field_size.x)+1):
        field[Vector2(x, -1)] = [CID_WALL, config.FOG_ENABLED, randint(0, 99), None]
        field[Vector2(x, field_size.y)] = [CID_WALL, config.FOG_ENABLED, randint(0, 99), None]

    for y in range(0, int(field_size.y)):
        field[Vector2(-1, y)] = [CID_WALL, config.FOG_ENABLED, randint(0, 99), None]
        field[Vector2(field_size.x, y)] = [CID_WALL, config.FOG_ENABLED, randint(0, 99), None]

    # создание выхода
    while True:
        key = cellsWithTable[randint(0, len(cellsWithTable) - 1)]
        if field[key - Vector2(0, 1)][CELL_ID] == CID_WALL:
            break
        cellsWithTable.remove(key)
    field[key][CELL_ID] = CID_EXIT

    return field
