"""
Файл служит для предотвращения циклического импорта модулей связанных с рендером
Он отвечает за хранение и использование необходимых классов и констант
"""

import pygame
from typing import Optional


pygame.font.init()

surface: Optional[pygame.surface.Surface] = None
defaultCellSize = None

font = pygame.font.get_default_font()
FONT_COMMON = pygame.font.Font(font, 20)
FONT_TITLE = pygame.font.Font(font, 40)
FONT_QUESTION = pygame.font.Font(font, 15)

LTYPE_UNKNOWN = -1
LTYPE_MAIN_MENU = 0
LTYPE_SETTINGS = 1
LTYPE_QUESTION = 2
LTYPE_PAUSE = 3
LTYPE_ENDGAME = 4


# дополнение вектора для возможности представить его как хеш
# необходимо для ориентации координат в пространстве лабиринта (field[Vector2(x, y)])
class Vector2(pygame.math.Vector2):
    def __hash__(self):
        return hash((self.x, self.y))


class Texture:
    """
    Класс для реализации текстуры
    """
    size: Vector2 = None
    file: str = None
    surface: pygame.surface.Surface = None

    def __init__(self, file: str, size: Vector2 = defaultCellSize):
        """
        :param file: Файл с текстурой
        :param size: Конечный размер текстуры. По умолчанию использует данные из конфигурации
        """
        self.file = file
        self.size = size
        if size == Vector2(0, 0):
            self.surface = pygame.image.load(file)
        else:
            self.surface = pygame.transform.scale(pygame.image.load(file), size)

    def Render(self, dest: Vector2):
        """
        Отображает текстуру без обновления содержимого на экране
        :param dest: Координата, куда наносится текстура
        """
        surface.blit(self.surface, dest)

    def SetFile(self, newFile: str, newSize: Optional[Vector2] = None):
        """
        Изменить файл текстуры
        :param newFile: Новый файл с текстурой
        :param newSize: Новый размер. По умолчанию используется старый размер
        """
        self.file = newFile
        if newSize is not None:
            self.size = newSize
        self.surface = pygame.transform.scale(pygame.image.load(newFile), self.size)


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
