"""
Файл служит для создания NPC(учителя) и его передвижения по лабиринту
"""
import render
import config
from renderProxy import *
from random import randint
from maze import GetDirections, CID_ROAD, MazeField


class Teacher:
    """
    Класс с самим NPC
    """
    pos: Vector2 = None  # позиция NPC
    prevPos: Vector2 = None  # предыдущая позиция NPC
    field = None  # массив с лабиринтом
    peaceMode: bool = False  # мирный режим

    forkData = [Vector2(-1, -1), []]  # данные о развилке
    # Первый элемент - позиция развилки
    # Второй - её возможные пути для посещения, в которых NPC еще не был

    def __init__(self, field, spawnPos):
        """
        :param MazeField field: Массив с лабиринтом, по которому будет ходить NPC
        :param Vector2 spawnPos: Начальная позиция, где разместить NPC
        """
        self.pos = spawnPos
        self.field = field

    # Передвинуть NPC, но не нарисовать его
    def Move(self):
        """
        Передвинуть NPC в случайном направлении
        Эта функция сама определяет направления, текущее направление и данные о развилках
        """
        directions = GetDirections(self.field, self.pos, CID_ROAD, config.MAZE_SIZE, False)

        # случай с тупиком. Двигаемся обратно
        if len(directions) == 1:
            self.prevPos = self.pos
            self.pos = self.pos + directions[0]
            return

        # убираем то направление, где мы уже были(возможный разворот на ровном месте)
        for v in directions:
            newPos = self.pos + v
            if newPos == self.prevPos:
                directions.remove(v)
                break

        # а теперь фильтруем развилку. Длинна массива теперь количество возможных путей(отфильтровали)
        direction = None
        if len(directions) >= 2:
            if self.forkData[0] != self.pos:
                # новая развилка. Старую забываем, новую запоминаем
                self.forkData[0] = self.pos
                self.forkData[1] = directions.copy()
            elif len(self.forkData[1]) == 0:
                # сюрприз. Мы вернулись к старой развилке. Обновляем возможные пути для развилки
                self.forkData[1] = directions.copy()
            direction = self.forkData[1][randint(0, len(self.forkData[1]) - 1)]
            self.forkData[1].remove(direction)
        else:
            # это коридор, развилок нет
            direction = directions[randint(0, len(directions) - 1)]

        # двигаемся по тому, что определили
        self.prevPos = self.pos
        self.pos = self.pos + direction

    # отрисовка NPC
    def Render(self, playerPos, frame):
        """
        Нарисовать NPC на экране
        :param Vector2 playerPos: Позиция игрока. Относительно неё будет идти рендер
        :param frame: Номер текущего кадра для создания анимации
        """
        c = (self.pos - playerPos) * config.CELL_SIZE - config.IMAGES["teacher"]["frameSize"]/2 + config.SCREEN_SIZE / 2
        if 0 < c.x < config.SCREEN_SIZE.x and 0 < c.y < config.SCREEN_SIZE.y:
            render.RenderAnimated("teacher", frame, c - Vector2(0, config.CELL_SIZE/2))
