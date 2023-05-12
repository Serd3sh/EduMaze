from config import Vector2
from random import randint
import config
import maze
import pygame
import render


class Teacher:
    pos: Vector2 = None  # позиция NPC
    prevPos: Vector2 = None  # предыдущая позиция NPC
    field = None  # массив с лабиринтом
    peaceMode: bool = False

    forkData = [Vector2(-1, -1), []]  # данные о развилке
    # Первый элемент - позиция развилки
    # Второй - её возможные пути для посещения, в которых NPC еще не был

    def __init__(self, field, spawnPos):
        self.pos = spawnPos
        self.field = field

    # Передвинуть NPC, но не нарисовать его
    def Move(self):
        directions = maze.GetDirections(self.field, self.pos, maze.ROAD, False)

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
            # дваложка. Это коридор, развилок нет
            direction = directions[randint(0, len(directions) - 1)]

        # оч сложна. Двигаемся по тому, что определили
        self.prevPos = self.pos
        self.pos = self.pos + direction

    # отрисовка NPC. Не поддерживает пока что туман войны
    def Render(self, playerPos):
        c = (self.pos - playerPos) * config.CELL_SIZE + config.SCREEN_SIZE / 2
        if 0 < c.x < config.SCREEN_SIZE.x and 0 < c.y < config.SCREEN_SIZE.y:
            pygame.draw.circle(render.surface, (255, 0, 0), c, 20)
