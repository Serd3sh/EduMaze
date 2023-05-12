import pygame
import maze
import config
from config import Vector2
from typing import Optional

# инициализация библиотек
pygame.font.init()
pygame.display.init()

# шрифты
font = pygame.font.get_default_font()
FONT_COMMON = pygame.font.Font(font, 20)
FONT_TITLE = pygame.font.Font(font, 40)
FONT_QUESTION = pygame.font.Font(font, 15)

# типы кнопок дли их идентификации при взаимодействии
LTYPE_UNKNOWN = -1
LTYPE_MAIN_MENU = 0
LTYPE_SETTINGS = 1
LTYPE_QUESTION = 2
LTYPE_PAUSE = 3

surface = pygame.display.set_mode(config.SCREEN_SIZE)
field: Optional[maze.MazeField] = None


class Label:
    """
    Класс для создания и взаимодействия с надписями
    """
    # "public" поля(свойства)
    pos: Vector2 = None
    text: str = None
    color: tuple[int, int, int] = None
    size: Vector2 = None
    type: int = LTYPE_UNKNOWN

    # "private" поля(служебные)
    __font: pygame.font.Font = None
    __wrappingLines: list[pygame.Surface] = []
    __obj: pygame.Surface = None

    # "private" функция для создания переносимых строк
    def __CalculateWrapping(self, wrapLen):
        if wrapLen <= 0:
            return
        self.__wrappingLines.clear()
        words = self.text.split(" ")
        lines = [""]
        line = 0
        for i in range(0, len(words)):
            add = lines[line] + ("" if len(lines[line]) == 0 else " ") + words[i]
            if self.__font.size(add)[0] >= wrapLen:
                line = line + 1
                lines.append(words[i])
            else:
                lines[line] = add

        for line in lines:
            self.__wrappingLines.append(self.__font.render(line, True, self.color))

    def __init__(self, text, pos, color, font=FONT_COMMON, wrapLen=0, LType=LTYPE_UNKNOWN):
        """
        :param str text: Наносимый текст
        :param Vector2 | tuple[float, float] pos: Позиция надписи
        :param tuple[int, int, int] color: Цвет надписи
        :param pygame.font.Font font: Используемый шрифт
        :param int wrapLen: Максимальная ширина надписи в пикс. Излишки переносятся на новую строку
        :param int LType: Тип надписи для идентификации динамических надписей(ответы к вопросам)
        """
        self.type = LType
        self.pos = pos
        self.text = text
        self.color = color
        self.__font = font
        self.__obj = font.render(text, True, color)
        self.size = Vector2(self.__obj.get_size())
        self.__CalculateWrapping(wrapLen)

    def ChangeText(self, text, wrapLen=0):
        """
        Изменяет текст отображаемой надписи
        :param str text: Новый текст
        """
        self.__obj = self.__font.render(text, True, self.color)
        self.__CalculateWrapping(wrapLen)

    def Render(self):
        """
        Отображает текст без обновления содержимого на экране
        """
        surface.blit(self.__obj, self.pos)

    def RenderWrapping(self):
        """
        Отображает текст с переносом строк без обновления содержимого на экране
        """
        for i in range(0, len(self.__wrappingLines)):
            surface.blit(self.__wrappingLines[i], self.pos + Vector2(0, i * self.__font.get_height()))

    def CollideWith(self, checkPos):
        """
        Проверить находится ли указанная точка внутри надписи(актуально для кнопок)
        :param Vector2 | tuple[int, int] checkPos: Проверяемая точка
        """
        if type(checkPos) == Vector2:
            return self.pos.x <= checkPos.x <= self.pos.x + self.size.x \
                and self.pos.y <= checkPos.y <= self.pos.y + self.size.y
        else:
            return self.pos.x <= checkPos[0] <= self.pos.x + self.size.x \
                and self.pos.y <= checkPos[1] <= self.pos.y + self.size.y


def RenderAnimated(img, frame, pos):
    """
    Рендер анимированной текстуры. Функция сама определяет какой кадр показать в зависимости от счетчика кадров
    :param str img: Наименование картинки из конфигурации
    :param int frame: Номер кадра, относительно которого будет идти выбор фрагментв для анимации
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


def RenderMaze(pos: Vector2):
    """
    Рендер фрагмента поля лабиринта, пределы которого определятся тем, что видит игрок
    Так же, обращает внимание на туман войны
    :param Vector2 pos: Позиция игрока внутри лабиринта
    """
    if field is None:
        return

    field[pos][maze.CELL_FOG] = False

    # рассеивание тумана войны по свободным 4 направлениям
    # тут происходит показ всего коридора, который должен видеть игрок
    for i in range(0, 4):
        tempPos = pos.copy()
        while True:
            tempPos += maze.directions[i] / 2
            if 0 <= tempPos.x < config.MAZE_SIZE.x and 0 <= tempPos.y < config.MAZE_SIZE.y \
                    and field[tempPos][maze.CELL_ID] == maze.ROAD:
                field[tempPos][maze.CELL_FOG] = False
                if tempPos.x + 1 < config.MAZE_SIZE.x:
                    field[tempPos + Vector2(1, 0)][maze.CELL_FOG] = False
                if tempPos.y + 1 < config.MAZE_SIZE.y:
                    field[tempPos + Vector2(0, 1)][maze.CELL_FOG] = False
                if tempPos.x - 1 > 0:
                    field[tempPos + Vector2(-1, 0)][maze.CELL_FOG] = False
                if tempPos.y - 1 > 0:
                    field[tempPos + Vector2(0, -1)][maze.CELL_FOG] = False
            else:
                break

    # рассеивание тумана вокруг игрока
    for y in range(int(pos.y - (config.RENDER_FOG - 1) / 2), int(pos.y + (config.RENDER_FOG + 1) / 2)):
        if y < 0 or y >= config.MAZE_SIZE.y:
            continue
        for x in range(int(pos.x - (config.RENDER_FOG - 1) / 2), int(pos.x + (config.RENDER_FOG + 1) / 2)):
            if x < 0 or x >= config.MAZE_SIZE.x:
                continue
            field[Vector2(x, y)][maze.CELL_FOG] = False

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
            if x < 0 or x >= config.MAZE_SIZE.x or field[Vector2(x, y)][maze.CELL_FOG]:
                continue
            surface.blit(field[Vector2(x, y)][maze.CELL_OBJ], (j * config.CELL_SIZE, i * config.CELL_SIZE))


def PreloadMazeTextures():
    """
    Подгрузка текстур в массив с лабиринтом для дальнейшего рендера
    :return:
    """
    for y in range(0, int(config.MAZE_SIZE.y)):
        for x in range(0, int(config.MAZE_SIZE.x)):
            currentCell = field[Vector2(x, y)]
            cellId = currentCell[maze.CELL_ID]
            randomIndex = currentCell[maze.CELL_RAND]
            if cellId == maze.WALL and y + 1 < config.MAZE_SIZE.y and field[Vector2(x, y + 1)][maze.CELL_ID] == maze.ROAD:
                if y - 1 >= 0 and field[Vector2(x, y - 1)][maze.CELL_ID] == maze.WALL:
                    currentCell[maze.CELL_OBJ] = GetRandom("surface_wall_door", randomIndex)
                else:
                    currentCell[maze.CELL_OBJ] = GetRandom("surface_wall", randomIndex)
            elif cellId == maze.WALL:
                currentCell[maze.CELL_OBJ] = GetRandom("wall", randomIndex)
            else:
                currentCell[maze.CELL_OBJ] = GetRandom("road", randomIndex)
