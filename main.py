"""
Главный файл. Использует вспомогательные файлы и отвечает за весь контроль игры
"""
import pygame.draw

import maze
import render
import sound
import teacher
import time
import config
from random import randint
from renderProxy import *

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
HP = 3
peaceMode = False

# переменные без значений по умолчанию(None, пустые массивы)
prevWindow: Optional[int] = None  # предыдущее активное окно
currentQuestion: Optional[str] = None  # текущая формулировка вопроса(идентификация при рендере и ответе на вопрос)
npc: [Optional[teacher.Teacher]] = []
mousePos: Optional[tuple[int, int]] = None  # позиция мыши для вычислений
hoverButton: Optional[list[Label]] = None  # текущая кнопка, на которой находится мышь
prevHoverButton: Optional[list[Label]] = None  # предыдущая кнопка, на которой находилась мышь
questionGiver: Optional[any] = None


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
UI_pauseLabel = Label(text="Пауза",  # большая надпись заголовка паузы
                      pos=config.SCREEN_SIZE / 2 - Vector2(FONT_TITLE.size("Пауза")) / 2 - Vector2(0, (1 + int(len(
                          pauseButtons) / 2)) * 30),
                      color=(255, 255, 255), font=FONT_TITLE, LType=LTYPE_PAUSE)
ui_question: Optional[Label] = None  # объект надписи вопроса
ui_answers: list[list[Label]] = []  # объекты надписей ответов

# Главное меню: кнопки
for i in range(0, len(mainMenuButtons)):
    y = config.SCREEN_SIZE.y - 25 * (len(mainMenuButtons) + 1) + 25 * i
    UI_mainMenuButtons.append([
        Label(text=mainMenuButtons[i], pos=Vector2(38, y),
              color=(255, 255, 255), LType=LTYPE_MAIN_MENU),
        Label(text="> " + mainMenuButtons[i], pos=Vector2(20, y),
              color=(255, 0, 0), LType=LTYPE_MAIN_MENU)
    ])

# Настройки: кнопки < >
for i in range(0, len(settingsButtons) - 1):
    if i % 2 == 0:
        x = config.SCREEN_SIZE.x - 25 * (len(settingsButtons) + 1) - 50
        y = config.SCREEN_SIZE.y - 55 * (len(settingsButtons) + 1) + 25 * i
    else:
        x = config.SCREEN_SIZE.x - 25 * (len(settingsButtons) + 1) + 50
    UI_settingsButtons.append([
        Label(text=settingsButtons[i], pos=Vector2(x, y),
              color=(255, 255, 255), LType=LTYPE_SETTINGS),
        Label(text=settingsButtons[i], pos=Vector2(x, y),
              color=(255, 0, 0), LType=LTYPE_SETTINGS)
    ])

# Настройки: кнопка возврата в главное меню
y = config.SCREEN_SIZE.y - 25 * (len(settingsButtons) + 1) + 25 * (len(settingsButtons) - 1)
UI_settingsButtons.append([
    Label(text=settingsButtons[len(settingsButtons) - 1], pos=Vector2(38, y),
          color=(255, 255, 255), LType=LTYPE_SETTINGS),
    Label(text="> " + settingsButtons[len(settingsButtons) - 1], pos=Vector2(20, y),
          color=(255, 0, 0), LType=LTYPE_SETTINGS)
])

# Настройки: информационные надписи
for i in range(0, len(settingsLabels)):
    x = config.SCREEN_SIZE.x - 25 * (len(settingsButtons) + 1) - 250
    y = config.SCREEN_SIZE.y - 55 * (len(settingsButtons) + 1) + 25 * i + 25 * i * (i % 2)
    UI_settingsLabels.append(Label(text=settingsLabels[i], pos=Vector2(x, y),
                                   color=(255, 255, 255), LType=LTYPE_SETTINGS))
    UI_settingsLabels.append(Label(text=str(int(sound.settingsSavedArray[i]*100)), pos=Vector2(x + 240, y),
                                   color=(255, 255, 255), LType=LTYPE_SETTINGS))

# Пауза
for i in range(0, len(pauseButtons)):
    y = config.SCREEN_SIZE.y / 2 + int(len(pauseButtons) / 2) * 30 * i
    x1 = config.SCREEN_SIZE.x / 2 - FONT_COMMON.size(pauseButtons[i])[0] / 2
    x2 = config.SCREEN_SIZE.x / 2 - FONT_COMMON.size("> " + pauseButtons[i] + " <")[0] / 2
    UI_pause.append([
        Label(text=pauseButtons[i], pos=Vector2(x1, y),
              color=(255, 255, 255), LType=LTYPE_PAUSE),
        Label(text="> " + pauseButtons[i] + " <", pos=Vector2(x2, y),
              color=(255, 0, 0), LType=LTYPE_PAUSE)
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
    pygame.draw.rect(surface, (0, 0, 0), (Vector2(0, 0), config.SCREEN_SIZE))


# основной цикл рендера
while runningGame:
    time.sleep(frameRate)
    frames = frames + 1
    mousePos = pygame.mouse.get_pos()
    if frames > 10000:
        frames = 0

    # демонстрация вопроса и пауза игры
    for bot in npc:
        if bot.pos == playerPos and not peaceMode:
            peaceMode = True
            ChangeWindow(WINDOW_QUESTION)
            questionGiver = bot
            break

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
                currentQuestion = questionKeys[randint(0, len(questionKeys) - 1)]
                ui_question = Label(text=currentQuestion, pos=Vector2(5, 5), color=(255, 192, 192),
                                    font=FONT_QUESTION, wrapLen=config.SCREEN_SIZE.x - 10)
                ui_answers.clear()
                for i in range(1, len(questions[currentQuestion])):
                    y = config.SCREEN_SIZE.y - 20 * len(questions[currentQuestion]) + 20 * i
                    ui_answers.append([
                        Label(text=str(i) + " " + questions[currentQuestion][i], pos=Vector2(20, y),
                              color=(255, 255, 255), font=FONT_QUESTION, LType=LTYPE_QUESTION),
                        Label(text="> " + questions[currentQuestion][i], pos=Vector2(20, y),
                              color=(255, 0, 0), font=FONT_QUESTION, LType=LTYPE_QUESTION)
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
                    for n in range(0, config.NPC_SPAWN_COUNT):
                        x = randint(0, config.MAZE_SIZE.x)
                        y = randint(0, config.MAZE_SIZE.y)
                        npc.append(teacher.Teacher(render.field, Vector2(x - x % 2, y - y % 2)))
                playerPos = Vector2(0, 0)
                hoverButton = None
                prevHoverButton = None
            elif hoverButton[0].text == "Назад":
                ChangeWindow(prevWindow)
                sound.SaveToFile()
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
            elif hoverButton[0].type == LTYPE_QUESTION:
                questionData = questions[currentQuestion]
                correct = int(hoverButton[0].text[:1]) == questionData[0]
                sound.PlaySound(sound.SOUND_Q_CORRECT if correct else sound.SOUND_Q_INCORRECT)
                if type(questionGiver) == list:  # если это стол - то questGiver будет информацией об этой клетке
                    if correct:
                        HP += 1
                    questionGiver[maze.CELL_ID] = maze.CID_TABLE
                    questionGiver[maze.CELL_OBJ].SetFile("assets/images/EmptyTable.png")
                else:  # а здесь уже NPC
                    if not correct:
                        HP -= 1
                questionGiver = None
                questions.pop(currentQuestion)
                if len(questions) == 0:
                    questions = config.QUESTIONS.copy()
                for bot in npc:
                    bot.Move()
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
        if maze.IsCellRoadType(render.field[checkPos][maze.CELL_ID]) or not config.COLLISIONS:
            playerPos = checkPos
            print(render.field[checkPos][maze.CELL_ID])

    # далее - рендер текстур лабиринта. Если это меню, дальше идти не стоит
    if currentWindow != WINDOW_GAME:
        continue

    # TODO: пустые столы тоже дают вопросы
    if currentWindow == WINDOW_GAME and render.field[playerPos][maze.CELL_ID] == maze.CID_PAPER_TABLE:
        peaceMode = True
        ChangeWindow(WINDOW_QUESTION)
        questionGiver = render.field[playerPos]

    # контроль выхода
    if currentWindow == WINDOW_GAME and render.field[playerPos][maze.CELL_ID] == maze.CID_EXIT:
        ChangeWindow(WINDOW_MAIN_MENU)
        render.field = None
        sound.StopSoundWalk()
        npc.clear()
        continue

    # очистка содержимого перед рендером и сам рендер
    ClearScreen()
    render.RenderMaze(playerPos, frames)
    render.RenderAnimated("player", frames, config.SCREEN_SIZE / 2 - Vector2(int(config.CELL_SIZE / 2),
                                                                             int(config.CELL_SIZE / 2)))
    if peaceMode:
        peaceFrames = peaceFrames + 1
    if peaceMode and peaceFrames == config.PEACE_COOLDOWN:
        peaceMode = False
        peaceFrames = 0
    for bot in npc:
        if frames % config.NPC_WALKSPEED == 0:  # каждый 5 кадр двигать NPC
            bot.Move()
        if not render.field[bot.pos][maze.CELL_FOG]:
            bot.Render(playerPos, frames)

    # TODO: при 0 HP игра окончена
    for i in range(0, HP):
        config.IMAGES["HP_protected" if peaceMode else "HP"][0][1].Render(
            Vector2(config.SCREEN_SIZE.x - (32+4)*(HP-i), 4))

    pygame.display.update()

pygame.quit()
