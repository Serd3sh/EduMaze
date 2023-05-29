"""
Конфигурация для более удобного дебага и изменения игровых правил
"""
from renderProxy import Vector2

# перегрузка хеширования вектора для возможности использовать вектор как индекс массива
NPC_ENABLED = True           # Спавн NPC
NPC_WALKSPEED = 5            # Скорость передвижения NPC в кадрах. Двигаться каждые NPC_WALKSPEED кадров(*)
NPC_SPAWN_COUNT = 3          # количество создаваемых NPC
PEACE_COOLDOWN = 100         # Длительность мирного режим в кадрах(*)
FOG_ENABLED = True           # показывать ли всю карту, или оставить туман войны
COLLISIONS = True            # разрешить игроку проходить сквозь стены
FPS = 30                     # фпс в секунду :>
RENDER_DIAMETER = 11         # количество клеток в ширину и в высоту отображаемое на экране(**)
RENDER_FOG = 3               # радиус показа карты вокруг игрока(**)
CELL_SIZE = 64               # размер одной клетки в пикс.
MAZE_SIZE = Vector2(15, 15)  # размер создаваемого лабиринта(**)
MIN_PAPER_TABLES = 3         # минимальное количество столов с заданиями при генерации
PAPER_TABLE_CHANCE = 50      # вероятность создания стола после достижения лимита MIN_PAPER_TABLES
SCREEN_SIZE = Vector2(CELL_SIZE, CELL_SIZE) * RENDER_DIAMETER  # не менять

# (*) - Не смотря на то, что FPS может стоять 30, за секунду пройдет меньше кадров
# Поэтому если таймер стоит условно на 60 кадров, пройти может больше 2 секунд(не более 3-4)
# Это связанно из-за технических особенностей

# (**) - Обязательно нечетная цифра(-ы) из-за связанных с свойством особенностей

DEFAULT_CELL_SIZE = Vector2(CELL_SIZE, CELL_SIZE)
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
        [0, "assets/images/Roof.png"]
    ],
    "surface_wall": [
        [0, "assets/images/SurfaceWallBlank.png"],
        [40, "assets/images/SurfaceWallOld.png"],
        [93, "assets/images/SurfaceWallNotes.png"],
        [95, "assets/images/SurfaceWallElectricPanel.png"],
        [97, "assets/images/SurfaceWallGOST.png"],
        [99, "assets/images/SurfaceWallKapibara.png"]
    ],
    "surface_wall_door": [
        [0, "assets/images/SurfaceWallBlank.png"],
        [80, "assets/images/SurfaceWallDoorNothing.png"],
        [85, "assets/images/SurfaceWallNothing.png"],
        [90, "assets/images/SurfaceWallNothing2.png"],
        [95, "assets/images/SurfaceWallDoor.png"]
    ],
    "road": [ [0, "assets/images/Road.png"] ],
    "exit": [ [0, "assets/images/Road.png"] ],
    "table": [ [0, "assets/images/EmptyTable.png"] ],
    "papers": [ [0, "assets/images/PapersTable.png"] ],

    "HP": [ [0, "assets/images/HP.png", DEFAULT_CELL_SIZE/2] ],
    "HP_protected": [ [0, "assets/images/HPProtected.png", DEFAULT_CELL_SIZE/2] ],

    # анимированная текстура представляется как выстроенные в линию спрайты(кадры)
    # спрайты лепятся друг к другу вплотную(воображаем бумажку и ножницы, как будем резать)
    "player": {
        "frameCount": 4,  # количество кадров в файле
        "length": 10,     # задержка кадра анимации в кадрах отрисовки (15 = 0.5 сек при 30FPS, 15/30)
        "file": "assets/images/character-animated.png",  # путь к файлу с текстурой
        "frameSize": DEFAULT_CELL_SIZE,  # размер одного кадра

        # служебные поля
        "frames": [],     # массив с кадрами в памяти
        "repeats": 0,     # количество текущих повторений
        "texture": None   # будущий объект текстуры
    },
    "teacher": {
        "frameCount": 4,
        "length": 10,
        "file": "assets/images/teacher-animated.png",
        "frameSize": DEFAULT_CELL_SIZE + Vector2(0, CELL_SIZE),

        "frames": [],
        "repeats": 0,
        "texture": None
    },
    "surface_exit": {
        "frameCount": 6,
        "length": 1,
        "file": "assets/images/ExitAnimated.png",
        "frameSize": DEFAULT_CELL_SIZE,

        "frames": [],
        "repeats": 0,
        "texture": None
    }
}

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
