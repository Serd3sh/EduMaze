import pygame

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()

# коды фоновой музыки
MUSIC_NONE = 0
MUSIC_MAIN_MENU = 1
MUSIC_GAME = 2

# коды звуков
SOUND_STEPS = pygame.mixer.Sound("sounds/Steps.mp3")
SOUND_BTN_CHANGE = pygame.mixer.Sound("sounds/Button change.mp3")
SOUND_BTN_PRESS = pygame.mixer.Sound("sounds/Button pressing.mp3")
SOUND_Q_CORRECT = pygame.mixer.Sound("sounds/Right answer.wav")
SOUND_Q_INCORRECT = pygame.mixer.Sound("sounds/Wrong answer.wav")
SOUND_EXIT = pygame.mixer.Sound("sounds/Exit.mp3")

VOL_MUSIC = 0
VOL_SOUND = 1

stepsChannel = pygame.mixer.Channel(0)  # канал для проигрывания шагов
soundChannel = pygame.mixer.Channel(1)  # канал для проигрывания других звуков
currentTrackCode: int = MUSIC_NONE  # флаг для музыки
volMusic: float = 1.0  # громкость музыки
volSound: float = 1.0  # громкость звуков


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
        pygame.mixer.music.load("sounds/Main Menu.mp3")
    elif currentTrackCode == MUSIC_GAME:
        pygame.mixer.music.load("sounds/GameOST.wav")

    if currentTrackCode != MUSIC_NONE:  # если мы по итогу загрузили новую композицию, значит её надо включить
        pygame.mixer.music.play(-1)  # -1 означает, что музыка будет играть бесконечное время. Т.е. самозапсукаться


def SetVolume(volType, newValue):
    """
    Изменяет громкость музки или звуков
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


# Синхронизация громкости
SetVolume(VOL_MUSIC, volMusic)
SetVolume(VOL_SOUND, volSound)