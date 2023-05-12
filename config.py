import pygame


# перегрузка хеширования вектора для возможности использовать вектор как индекс массива
class Vector2(pygame.math.Vector2):
    def __hash__(self):
        return hash((self.x, self.y))


NPC_ENABLED = True           # Спавн NPC
NPC_WALKSPEED = 5            # Скорость передвижения NPC в кадрах. Двигаться каждые NPC_WALKSPEED кадров(*)
PEACE_COOLDOWN = 100         # Длительность мирного режим в кадрах(*)
FOG_ENABLED = True           # показывать ли всю карту, или оставить туман войны
COLLISIONS = True            # разрешить игроку проходить сквозь стены
FPS = 30                     # фпс в секунду :>
RENDER_DIAMETER = 11         # количество клеток в ширину и в высоту отображаемое на экране(**)
RENDER_FOG = 3               # радиус показа карты вокруг игрока(**)
CELL_SIZE = 64               # размер одной клетки в пикс.
MAZE_SIZE = Vector2(15, 15)  # размер создаваемого лабиринта(**)
SCREEN_SIZE = Vector2(CELL_SIZE, CELL_SIZE) * RENDER_DIAMETER  # не менять

# (*) - Не смотря на то, что FPS может стоять 30, за секунду пройдет меньше кадров
# Поэтому если таймер стоит условно на 60 кадров, пройти может больше 2 секунд(не более 3-4)
# Это связанно из-за технических особенностей

# (**) - Обязательно нечетная цифра(-ы) из-за связанных с свойством особенностей


QUESTIONS = {
    # Вопрос: [правильный номер ответа, ответ1, ответ2, ..., ответN]
    "Question1": [
        3, "A1",
        "A2",
        "A3(correct)",
        "A4"
    ],
    "При чтении недоступного адреса памяти...": [
        2, "Ничего не произойдет",
        "Программа выдаст ошибку и остановится",
        "Программа вернет записанное значение"
    ],
    "Вопрос2": [
        1, "Ответ1(верный)",
        "Ответ2",
        "Ответ3",
        "Ответ4"
    ],
    "Что произойдет, если написать for (;;) {code}": [
        3, "Такая инструкция недопустима",
        "Зависит от обстоятельств",
        "Бесконечный цикл",
        "Капибара"
    ],
    "В C# все работает на классах и объектах": [
        1, "Верно", "Неверно"
    ]
}

IMAGES = {
    # "тип клетки": [граничное случайное число, путь к файлу]
    # рандом работает на случайном числе, которое генерируется в пределах [0, 100)
    # при загрузке прога создает это число и ищет ближайшее наименьшее среди этой кучи

    # Пример:
    # [0, "pic1.png"]  - [0, 10). В промежутке 10 чисел = шанс 10%
    # [10, "pic2.png"] - [10, 40). Аналогично. Шанс = 40-10 = 30%
    # [40, "pic3.png"] - [40, 85). Шанс = 85-49 = 45%
    # [85, "pic4.png"] - [85, 100). Шанс = 100-85 + 1 = 15%

    # элементы размещать СТРОГО в возрастающем порядке по числам
    # в случае нескольких файлов рекомендуется нумеровать с 0
    # использование анимированных GIF не допускается из-за особенности библиотеки SDL(pygame)
    "wall": [
        [0, "assets/Roof.png"]
    ],
    "surface_wall": [
        [0, "assets/SurfaceWallBlank.png"],
        [40, "assets/SurfaceWallOld.png"],
        [93, "assets/SurfaceWallNotes.png"],
        [95, "assets/SurfaceWallElectricPanel.png"],
        [97, "assets/SurfaceWallGOST.png"],
        [99, "assets/SurfaceWallKapibara.png"]
    ],
    "surface_wall_door": [
        [0, "assets/SurfaceWallBlank.png"],
        [80, "assets/SurfaceWallDoorNothing.png"],
        [85, "assets/SurfaceWallNothing.png"],
        [90, "assets/SurfaceWallNothing2.png"],
        [95, "assets/SurfaceWallDoor.png"]
    ],
    "road": [
        [0, "assets/Road.png"]
    ],

    # анимированная текстура представляется как выстроенные в линию спрайты(кадры)
    # спрайты лепятся друг к другу вплотную(воображаем бумажку и ножницы, как будем резать)
    "player": {
        "frameCount": 4,  # количество кадров в файле
        "frames": [],     # не записывать. Нужно для подгрузки кадров в память
        "repeats": 0,     # не изменять. Нужно для запоминания задержки
        "length": 10,     # задержка кадра анимации в кадрах отрисовки (15 = 0.5 сек при 30FPS, 15/30)
        "surface": pygame.transform.scale(
            pygame.image.load("assets/character-animated.png"),
            Vector2(CELL_SIZE * 4, CELL_SIZE)
        )
    }
}


# загрузка изображения с подгоном разрешения
def load(root: list):
    for key in root:
        key[1] = pygame.transform.scale(pygame.image.load(key[1]), Vector2(CELL_SIZE, CELL_SIZE))


load(IMAGES["wall"])
load(IMAGES["surface_wall"])
load(IMAGES["surface_wall_door"])
load(IMAGES["road"])

# загрузка анимации. То есть, подготовка массива с кадрами
for key in IMAGES:
    data = IMAGES[key]
    if type(data) != dict:
        continue
    for i in range(0, data["frameCount"]):
        data["frames"].append(data["surface"].subsurface(i * CELL_SIZE, 0, CELL_SIZE, CELL_SIZE))
