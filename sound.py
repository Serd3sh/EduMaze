"""
Файл служит для подгрузки и использования звуков в игре
"""
from array import array
from os import stat
from os.path import exists
import pygame

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()

# коды фоновой музыки
MUSIC_NONE = 0
MUSIC_MAIN_MENU = 1
MUSIC_GAME = 2

# коды звуков
SOUND_STEPS = pygame.mixer.Sound("assets/sounds/Steps.mp3")
SOUND_BTN_CHANGE = pygame.mixer.Sound("assets/sounds/Button change.mp3")
SOUND_BTN_PRESS = pygame.mixer.Sound("assets/sounds/Button pressing.mp3")
SOUND_Q_CORRECT = pygame.mixer.Sound("assets/sounds/Right answer.wav")
SOUND_Q_INCORRECT = pygame.mixer.Sound("assets/sounds/Wrong answer.wav")
SOUND_EXIT = pygame.mixer.Sound("assets/sounds/Exit.mp3")

# константы при обращении из вне
VOL_MUSIC = 0
VOL_SOUND = 1

# загрузка сохраненных значений
settingsSavedArray = array('f')
if not exists("settings.bin") or stat("settings.bin").st_size == 0:
    settingsSavedArray.append(1.0)
    settingsSavedArray.append(1.0)
else:
    settingsFile = open("settings.bin", "rb")
    settingsSavedArray.fromfile(settingsFile, 2)
    settingsFile.close()

stepsChannel = pygame.mixer.Channel(0)  # канал для проигрывания шагов
soundChannel = pygame.mixer.Channel(1)  # канал для проигрывания других звуков
currentTrackCode: int = MUSIC_NONE  # флаг для музыки
volMusic: float = settingsSavedArray[VOL_MUSIC]  # громкость музыки
volSound: float = settingsSavedArray[VOL_SOUND]  # громкость звуков


def PlaySound(sound):
    """
    Воспроизведение звука
    :param pygame.mixer.Sound sound: Загруженный файл со звуком для воспроизведения
    """
    if sound == SOUND_STEPS:
        if not stepsChannel.get_busy():
            stepsChannel.play(SOUND_STEPS)
    else:
        soundChannel.play(sound)


def StopSoundWalk():
    """
    Прекращение проигрывания звука шагов
    """
    stepsChannel.stop()  # пауза с очисткой


def ChangeMusic(newTrackCode):
    """
    Смена музыки
    :param newTrackCode: Код музыки, которую необходимо включить
    """
    global currentTrackCode
    if currentTrackCode == newTrackCode:
        return

    currentTrackCode = newTrackCode
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()

    if currentTrackCode == MUSIC_MAIN_MENU:
        pygame.mixer.music.load("assets/sounds/Main Menu.mp3")
    elif currentTrackCode == MUSIC_GAME:
        pygame.mixer.music.load("assets/sounds/GameOST.wav")

    if currentTrackCode != MUSIC_NONE:  # если мы по итогу загрузили новую композицию, значит её надо включить
        pygame.mixer.music.play(-1)  # -1 означает, что музыка будет играть бесконечное время. Т.е. самозапсукаться


def SetVolume(volType, newValue):
    """
    Изменяет громкость музыки или звуков
    :param int volType: Тип звука: VOL_MUSIC | VOL_SOUND
    :param float newValue: Новое значение громкости [0; 1]
    """
    if volType == VOL_MUSIC:
        global volMusic
        volMusic = newValue
        pygame.mixer.music.set_volume(volMusic)
    elif volType == VOL_SOUND:
        global volSound
        volSound = newValue
        stepsChannel.set_volume(volSound)
        soundChannel.set_volume(volSound)

def SaveToFile():
    changed = False
    if settingsSavedArray[VOL_MUSIC] != volMusic:
        settingsSavedArray[VOL_MUSIC] = volMusic
        changed = True
    if settingsSavedArray[VOL_SOUND] != volSound:
        settingsSavedArray[VOL_SOUND] = volSound
        changed = True
    if changed:
        settingsFile = open("settings.bin", "wb+")
        settingsSavedArray.tofile(settingsFile)
        settingsFile.close()


# Синхронизация громкости
SetVolume(VOL_MUSIC, volMusic)
SetVolume(VOL_SOUND, volSound)
