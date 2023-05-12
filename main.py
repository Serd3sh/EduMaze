import random
import time
import pygame
import maze
import sound
import render
import config
import teacher
from config import Vector2
from typing import Optional

# идентификация активного окна
WINDOW_MAIN_MENU = 0
WINDOW_SETTINGS = 1
WINDOW_GAME = 2
WINDOW_PAUSE = 3
WINDOW_QUESTION = 4

# переменными со значениями по умолчанию
currentWindow = WINDOW_MAIN_MENU  # текущее активное окно
playerPos = Vector2(0, 0)  # позиция игрока внутри лабиринта
runningGame = True  # флаг выхода из игры(Х или выход в меню)
frames = 0  # счетчик кадров для ренедра анимации и скорости передвижения NPC
frameRate = 1 / config.FPS  # время задержки между кадрами для приостановки потока в рендере
peaceFrames = 0  # счетчик кадров мирного режима
questions = config.QUESTIONS.copy()  # массив с вопросами

# переменные без значений по умолчанию(None, пустые массивы)
prevWindow: Optional[int] = None  # предыдущее активное окно
currentQuestion: Optional[str] = None  # текущая формулировка вопроса(идентификация при рендере и ответе на вопрос)
npc: Optional[teacher.Teacher] = None  # будущий объект NPC
mousePos: Optional[tuple[int, int]] = None  # позиция мыши для вычислений
hoverButton: Optional[list[render.Label]] = None  # текущая кнопка, на которой находится мышь
prevHoverButton: Optional[list[render.Label]] = None  # предыдущая кнопка, на которой находилась мышь

# интерфейс
mainMenuButtons = ["Новая игра", "Настройки", "Выход"]
settingsButtons = ["<", ">", "<", ">", "Назад"]
settingsLabels = ["Громкость музыки:", "Громкость звуков:"]
pauseButtons = ["Продолжить", "Настройки", "Завершить игру"]
UI_mainMenuButtons = []  # массив с созданными кнопками главного меню
# UI = [[обычная, выделенная], [обычная, выделенная], ...]
UI_settingsButtons = []  # кнопки настроек
UI_settingsLabels = []  # надписи настроек
UI_pause = []  # кнопки паузы
UI_pauseLabel = render.Label(text="Пауза",  # большая надпись заголовка паузы
                             pos=config.SCREEN_SIZE / 2
                                 - Vector2(render.FONT_TITLE.size("Пауза")) / 2
                                 - Vector2(0, (1 + int(len(pauseButtons) / 2)) * 30),
                             color=(255, 255, 255), font=render.FONT_TITLE, LType=render.LTYPE_PAUSE)
ui_question: Optional[render.Label] = None  # объект надписи вопроса
ui_answers: list[list[render.Label]] = []  # объекты надписей ответов

# Главное меню: кнопки
for i in range(0, len(mainMenuButtons)):
    y = config.SCREEN_SIZE.y - 25 * (len(mainMenuButtons) + 1) + 25 * i
    UI_mainMenuButtons.append([
        render.Label(text=mainMenuButtons[i], pos=Vector2(38, y),
                     color=(255, 255, 255), LType=render.LTYPE_MAIN_MENU),
        render.Label(text="> " + mainMenuButtons[i], pos=Vector2(20, y),
                     color=(255, 0, 0), LType=render.LTYPE_MAIN_MENU)
    ])

# Настройки: кнопки < >
for i in range(0, len(settingsButtons) - 1):
    if i % 2 == 0:
        x = config.SCREEN_SIZE.x - 25 * (len(settingsButtons) + 1) - 50
        y = config.SCREEN_SIZE.y - 55 * (len(settingsButtons) + 1) + 25 * i
    else:
        x = config.SCREEN_SIZE.x - 25 * (len(settingsButtons) + 1) + 50
    UI_settingsButtons.append([
        render.Label(text=settingsButtons[i], pos=Vector2(x, y),
                     color=(255, 255, 255), LType=render.LTYPE_SETTINGS),
        render.Label(text=settingsButtons[i], pos=Vector2(x, y),
                     color=(255, 0, 0), LType=render.LTYPE_SETTINGS)
    ])

# Настройки: кнопка возврата в главное меню
y = config.SCREEN_SIZE.y - 25 * (len(settingsButtons) + 1) + 25 * (len(settingsButtons) - 1)
UI_settingsButtons.append([
    render.Label(text=settingsButtons[len(settingsButtons) - 1], pos=Vector2(38, y),
                 color=(255, 255, 255), LType=render.LTYPE_SETTINGS),
    render.Label(text="> " + settingsButtons[len(settingsButtons) - 1], pos=Vector2(20, y),
                 color=(255, 0, 0), LType=render.LTYPE_SETTINGS)
])

# Настройки: информационные надписи
for i in range(0, len(settingsLabels)):
    x = config.SCREEN_SIZE.x - 25 * (len(settingsButtons) + 1) - 250
    y = config.SCREEN_SIZE.y - 55 * (len(settingsButtons) + 1) + 25 * i + 25 * i * (i % 2)
    UI_settingsLabels.append(render.Label(text=settingsLabels[i], pos=Vector2(x, y),
                                          color=(255, 255, 255), LType=render.LTYPE_SETTINGS))
    UI_settingsLabels.append(render.Label(text='100', pos=Vector2(x + 240, y),
                                          color=(255, 255, 255), LType=render.LTYPE_SETTINGS))

# Пауза
for i in range(0, len(pauseButtons)):
    y = config.SCREEN_SIZE.y / 2 + int(len(pauseButtons) / 2) * 30 * i
    x1 = config.SCREEN_SIZE.x / 2 - render.FONT_COMMON.size(pauseButtons[i])[0] / 2
    x2 = config.SCREEN_SIZE.x / 2 - render.FONT_COMMON.size("> " + pauseButtons[i] + " <")[0] / 2
    UI_pause.append([
        render.Label(text=pauseButtons[i], pos=Vector2(x1, y),
                     color=(255, 255, 255), LType=render.LTYPE_PAUSE),
        render.Label(text="> " + pauseButtons[i] + " <", pos=Vector2(x2, y),
                     color=(255, 0, 0), LType=render.LTYPE_PAUSE)
    ])


def RenderButtons(array):
    """
    Рендер кнопок в соответствии с тем, куда указывает мышь
    Задает hoverButton, если мышь куда то наведена
    :param array: Массив с кнопками
    """
    global hoverButton, prevHoverButton
    for element in array:
        if element[1].CollideWith(mousePos):  # если мышь внутри кнопки
            if element != prevHoverButton:  # смотрим сменилась ли у нас кнопка
                sound.PlaySound(sound.SOUND_BTN_CHANGE)
                prevHoverButton = element  # если да, то отмечаем это изменение
            element[1].Render()
            hoverButton = element
        else:
            if element == prevHoverButton:
                prevHoverButton = None
            element[0].Render()


def ChangeWindow(newWindow):
    """
    Изменение текущего окна на новое с перезаписью prevWindow
    :param newWindow: Окно, которое необходимо показать
    """
    global prevWindow, currentWindow
    prevWindow = currentWindow
    currentWindow = newWindow


def ClearScreen():
    """
    Очистка экрана перед рендером
    """
    pygame.draw.rect(render.surface, (0, 0, 0), (Vector2(0, 0), config.SCREEN_SIZE))


# основной цикл рендера
while runningGame:
    time.sleep(frameRate)
    frames = frames + 1
    mousePos = pygame.mouse.get_pos()
    if frames > 10000:
        frames = 0

    # демонстрация вопроса и пауза игры
    if npc and npc.pos == playerPos and not npc.peaceMode:
        npc.peaceMode = True
        ChangeWindow(WINDOW_QUESTION)

    # рендер обычного интерфейса(не лабиринт)
    if currentWindow != WINDOW_GAME:
        if currentWindow != WINDOW_QUESTION:
            sound.ChangeMusic(sound.MUSIC_MAIN_MENU)
        ClearScreen()
        hoverButton = None
        if currentWindow == WINDOW_SETTINGS:
            RenderButtons(UI_settingsButtons)
            for element in UI_settingsLabels:
                element.Render()
        elif currentWindow == WINDOW_MAIN_MENU:
            RenderButtons(UI_mainMenuButtons)
        elif currentWindow == WINDOW_PAUSE:
            RenderButtons(UI_pause)
            UI_pauseLabel.Render()
        elif currentWindow == WINDOW_QUESTION:
            if not currentQuestion:
                questionKeys = list(questions.keys())
                currentQuestion = questionKeys[random.randint(0, len(questionKeys) - 1)]
                ui_question = render.Label(text=currentQuestion, pos=Vector2(5, 5), color=(255, 192, 192),
                                           font=render.FONT_QUESTION, wrapLen=config.SCREEN_SIZE.x - 10)
                ui_answers.clear()
                for i in range(1, len(questions[currentQuestion])):
                    y = config.SCREEN_SIZE.y - 20 * len(questions[currentQuestion]) + 20 * i
                    ui_answers.append([
                        render.Label(text=str(i) + " " + questions[currentQuestion][i], pos=Vector2(20, y),
                                     color=(255, 255, 255), font=render.FONT_QUESTION, LType=render.LTYPE_QUESTION),
                        render.Label(text="> " + questions[currentQuestion][i], pos=Vector2(20, y),
                                     color=(255, 0, 0), font=render.FONT_QUESTION, LType=render.LTYPE_QUESTION)
                    ])
            ui_question.RenderWrapping()
            RenderButtons(ui_answers)
        pygame.display.update()  # показ содержимого

    # контроль нажатия кнопок
    for ev in pygame.event.get():
        # сигнал закрытия окна через Х
        if ev.type == pygame.QUIT:
            runningGame = False
            break
        # контроль нажатия мыши в меню
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == pygame.BUTTON_LEFT:
            if hoverButton is None:
                continue
            sound.PlaySound(sound.SOUND_BTN_PRESS)
            if hoverButton[0].text == "Выход":
                runningGame = False
                break
            elif hoverButton[0].text == "Настройки":
                ChangeWindow(WINDOW_SETTINGS)
            elif hoverButton[0].text == "Новая игра":
                ChangeWindow(WINDOW_GAME)
                render.field = maze.GenerateMaze(config.MAZE_SIZE)
                render.PreloadMazeTextures()
                if config.NPC_ENABLED:
                    npc = teacher.Teacher(render.field, Vector2(2, 2))
                playerPos = Vector2(0, 0)
                hoverButton = None
                prevHoverButton = None
            elif hoverButton[0].text == "Назад":
                ChangeWindow(prevWindow)
                break
            elif hoverButton[0].text == "Продолжить":
                ChangeWindow(WINDOW_GAME)
                break
            elif hoverButton[0].text == "Завершить игру":
                ChangeWindow(WINDOW_MAIN_MENU)
                render.field = None
                sound.StopSoundWalk()
                break
            elif hoverButton[0].text == ">":
                if UI_settingsButtons[1][0].CollideWith(mousePos) and sound.volMusic < 1:
                    sound.SetVolume(sound.VOL_MUSIC, sound.volMusic + 0.1)
                    UI_settingsLabels[1].ChangeText(str(int(sound.volMusic * 100)))
                elif UI_settingsButtons[3][0].CollideWith(mousePos) and sound.volSound < 1:
                    sound.SetVolume(sound.VOL_SOUND, sound.volSound + 0.1)
                    UI_settingsLabels[3].ChangeText(str(int(sound.volSound * 100)))
            elif hoverButton[0].text == "<":
                if UI_settingsButtons[0][0].CollideWith(mousePos) and sound.volMusic > 0.1:
                    sound.SetVolume(sound.VOL_MUSIC, sound.volMusic - 0.1)
                    UI_settingsLabels[1].ChangeText(str(int(sound.volMusic * 100)))
                elif UI_settingsButtons[2][0].CollideWith(mousePos) and sound.volSound > 0.1:
                    sound.SetVolume(sound.VOL_SOUND, sound.volSound - 0.1)
                    UI_settingsLabels[3].ChangeText(str(int(sound.volSound * 100)))
            elif hoverButton[0].type == render.LTYPE_QUESTION:
                questionData = questions[currentQuestion]
                sound.PlaySound(sound.SOUND_Q_CORRECT if int(hoverButton[0].text[:1]) == questionData[0]
                                else sound.SOUND_Q_INCORRECT)
                questions.pop(currentQuestion)
                if len(questions) == 0:
                    questions = config.QUESTIONS.copy()
                npc.Move()
                currentQuestion = None
                ChangeWindow(WINDOW_GAME)

        # если лабиринта нет, значит запускать игру не нужно. Далее только контроль игры
        if currentWindow != WINDOW_GAME:
            continue

        sound.ChangeMusic(sound.MUSIC_GAME)
        # считываем только нажатые кнопки
        if ev.type != pygame.KEYDOWN:
            continue

        # считываем возможное передвижение по лабиринту с помощью стрелочек на клавиатуре
        checkPos = None
        if ev.key == pygame.K_RIGHT:
            sound.PlaySound(sound.SOUND_STEPS)
            checkPos = playerPos + Vector2(1, 0)
        elif ev.key == pygame.K_LEFT:
            sound.PlaySound(sound.SOUND_STEPS)
            checkPos = playerPos - Vector2(1, 0)
        elif ev.key == pygame.K_DOWN:
            sound.PlaySound(sound.SOUND_STEPS)
            checkPos = playerPos + Vector2(0, 1)
        elif ev.key == pygame.K_UP:
            sound.PlaySound(sound.SOUND_STEPS)
            checkPos = playerPos - Vector2(0, 1)
        # и, возможную паузу
        elif ev.key == pygame.K_ESCAPE and currentWindow == WINDOW_GAME:
            ChangeWindow(WINDOW_PAUSE)
            break
        else:
            continue

        # удостоверяемся в том, что мы не вышли за пределы лабиринта
        if checkPos.x < 0 or checkPos.y < 0 or checkPos.x >= config.MAZE_SIZE.x or checkPos.y >= config.MAZE_SIZE.y:
            continue

        # проверка коллизии со стеной
        if render.field[checkPos][maze.CELL_ID] == maze.ROAD or not config.COLLISIONS:
            playerPos = checkPos

    # контроль выхода
    if playerPos == config.MAZE_SIZE - Vector2(1, 1):
        render.field = None
        sound.StopSoundWalk()
        ChangeWindow(WINDOW_MAIN_MENU)
        continue

    # далее - рендер текстур лабиринта. Если это меню, дальше идти не стоит
    if currentWindow != WINDOW_GAME:
        continue

    # очистка содержимого перед рендером и сам рендер
    ClearScreen()
    render.RenderMaze(playerPos)
    render.RenderAnimated("player", frames, config.SCREEN_SIZE / 2 - Vector2(int(config.CELL_SIZE / 2),
                                                                             int(config.CELL_SIZE / 2)))
    if npc:
        if npc.peaceMode:
            peaceFrames = peaceFrames + 1
        if frames % config.NPC_WALKSPEED == 0:  # каждый 5 кадр двигать NPC
            npc.Move()
        if npc.peaceMode and peaceFrames == config.PEACE_COOLDOWN:
            npc.peaceMode = False
            peaceFrames = 0
        npc.Render(playerPos)

    pygame.display.update()

pygame.quit()
