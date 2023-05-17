"""
Файл служит для отрисовки подгрузки текстур и их дальнейшего использования
Умеет работать как со статическими текстурами, так и с анимированными
Все используемые константы и классы находятся в файле renderProxy.py
"""
import config
import maze
import renderProxy
from renderProxy import *
from maze import CELL_ID, CELL_OBJ, CELL_RAND, CELL_FOG, DIRECTIONS, ROAD, WALL


pygame.display.init()
surface = renderProxy.surface = pygame.display.set_mode(config.SCREEN_SIZE)


def RenderAnimated(img, frame, pos):
    """
    Рендер анимированной текстуры. Функция сама определяет какой кадр показать в зависимости от счетчика кадров
    :param str img: Наименование картинки из конфигурации
    :param int frame: Номер кадра, относительно которого будет идти выбор фрагмента для анимации
    :param Vector2 pos: Где разместить этот фрагмент(позиция экрана)
    """
    if frame % config.IMAGES[img]["length"] == 0:
        config.IMAGES[img]["repeats"] = (config.IMAGES[img]["repeats"] + 1) % config.IMAGES[img]["frameCount"]
    surface.blit(config.IMAGES[img]["frames"][config.IMAGES[img]["repeats"]], pos)


def GetRandom(img, randomIndex):
    """
    Определение случайной текстуры для текстур с шансом выпадения
    :param str img: Наименование текстуры из конфигурации
    :param int randomIndex: Случайное число, записанное в клетку
    :returns: Surface текстуры
    """
    path = config.IMAGES[img]
    res = path[0]
    for i in range(0, len(config.IMAGES[img])):
        if i == len(config.IMAGES[img]) - 1:
            if path[i][0] <= randomIndex:
                res = path[i]
        elif path[i][0] <= randomIndex <= path[i+1][0]:
            if path[i + 1][0] == randomIndex:
                res = path[i + 1]
            else:
                res = path[i]
            break

    return res[1]


field: Optional[maze.MazeField] = None


def RenderMaze(pos: Vector2):
    """
    Рендер фрагмента поля лабиринта, пределы которого определятся тем, что видит игрок
    Так же, обращает внимание на туман войны
    :param Vector2 pos: Позиция игрока внутри лабиринта
    """
    if field is None:
        return

    field[pos][CELL_FOG] = False

    # рассеивание тумана войны по свободным 4 направлениям
    # тут происходит показ всего коридора, который должен видеть игрок
    for i in range(0, 4):
        tempPos = pos.copy()
        while True:
            tempPos += DIRECTIONS[i] / 2
            if 0 <= tempPos.x < config.MAZE_SIZE.x and 0 <= tempPos.y < config.MAZE_SIZE.y \
                    and field[tempPos][CELL_ID] == ROAD:
                field[tempPos][CELL_FOG] = False
                if tempPos.x + 1 < config.MAZE_SIZE.x:
                    field[tempPos + Vector2(1, 0)][CELL_FOG] = False
                if tempPos.y + 1 < config.MAZE_SIZE.y:
                    field[tempPos + Vector2(0, 1)][CELL_FOG] = False
                if tempPos.x - 1 > 0:
                    field[tempPos + Vector2(-1, 0)][CELL_FOG] = False
                if tempPos.y - 1 > 0:
                    field[tempPos + Vector2(0, -1)][CELL_FOG] = False
            else:
                break

    # рассеивание тумана вокруг игрока
    for y in range(int(pos.y - (config.RENDER_FOG - 1) / 2), int(pos.y + (config.RENDER_FOG + 1) / 2)):
        if y < 0 or y >= config.MAZE_SIZE.y:
            continue
        for x in range(int(pos.x - (config.RENDER_FOG - 1) / 2), int(pos.x + (config.RENDER_FOG + 1) / 2)):
            if x < 0 or x >= config.MAZE_SIZE.x:
                continue
            field[Vector2(x, y)][CELL_FOG] = False

    # рендер лабиринта
    # i(y), j(x) - сдвиг клетки при рендере. Это имеет смысл, когда туман войны не позволяет нарисовать клетку
    (i, j) = (-1, -1)
    for y in range(int(pos.y - (config.RENDER_DIAMETER - 1) / 2), int(pos.y + (config.RENDER_DIAMETER + 1) / 2)):
        i = i + 1
        j = -1
        if y < 0 or y >= config.MAZE_SIZE.y:
            continue
        for x in range(int(pos.x - (config.RENDER_DIAMETER - 1) / 2), int(pos.x + (config.RENDER_DIAMETER + 1) / 2)):
            j = j + 1
            if x < 0 or x >= config.MAZE_SIZE.x or field[Vector2(x, y)][CELL_FOG]:
                continue
            field[Vector2(x, y)][CELL_OBJ].Render(Vector2(j * config.CELL_SIZE, i * config.CELL_SIZE))


def PreloadMazeTextures():
    """
    Подгрузка текстур в массив с лабиринтом для дальнейшего рендера
    :return:
    """
    for y in range(0, int(config.MAZE_SIZE.y)):
        for x in range(0, int(config.MAZE_SIZE.x)):
            currentCell = field[Vector2(x, y)]
            cellId = currentCell[CELL_ID]
            randomIndex = currentCell[CELL_RAND]
            if cellId == WALL and y + 1 < config.MAZE_SIZE.y and field[Vector2(x, y + 1)][CELL_ID] == ROAD:
                if y - 1 >= 0 and field[Vector2(x, y - 1)][CELL_ID] == WALL:
                    currentCell[CELL_OBJ] = GetRandom("surface_wall_door", randomIndex)
                else:
                    currentCell[CELL_OBJ] = GetRandom("surface_wall", randomIndex)
            elif cellId == WALL:
                currentCell[CELL_OBJ] = GetRandom("wall", randomIndex)
            else:
                currentCell[CELL_OBJ] = GetRandom("road", randomIndex)


# замена путей к текстурам в конфиге на сами текстуры, подготовка анимаций
for key in config.IMAGES:
    data = config.IMAGES[key]
    if type(data) == dict:  # словарь использует анимированная текстура, в то время как обычная текстура - список
        data["texture"] = Texture(data["file"], Vector2(data["frameSize"].x * data["frameCount"], data["frameSize"].y))
        for i in range(0, data["frameCount"]):
            data["frames"].append(data["texture"].surface.subsurface(
                i * config.CELL_SIZE, 0, data["frameSize"].x, data["frameSize"].y))
    else:
        for obj in data:
            obj[1] = Texture(obj[1], config.DEFAULT_CELL_SIZE)