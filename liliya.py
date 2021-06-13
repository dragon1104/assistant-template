import subprocess, sys
sys.path.append('mainmodules/')
from vosk import Model, KaldiRecognizer
import os, json, re, threading, signal, shutil, time
from botname import isbotname
from mainai import getanswer
import pyaudio, keyboard

from pygame import mixer
mixer.init()

oldtime=int(time.time())
sluh=0
# Время через которое Лилия перестает слушать
stoptime=60

# Путь до файла JSON полученного в Google Cloud
put=os.getcwd()+"\yourkey.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = put
from google.cloud import texttospeech
client = texttospeech.TextToSpeechClient()
voice = texttospeech.VoiceSelectionParams(
    language_code="ru-RU", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
)
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3
)

import win32api, win32con, time, os.path, inspect, sys
from ctypes import *
user32 = windll.user32
kernel32 = windll.kernel32


def get_script_dir(follow_symlinks=True):
    if getattr(sys, 'frozen', False): # py2exe, PyInstaller, cx_Freeze
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_script_dir)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)


class RECT(Structure):
    _fields_ = [
        ("left", c_ulong),
        ("top", c_ulong),
        ("right", c_ulong),
        ("bottom", c_ulong)
    ]


class GUITHREADINFO(Structure):
    _fields_ = [
        ("cbSize", c_ulong),
        ("flags", c_ulong),
        ("hwndActive", c_ulong),
        ("hwndFocus", c_ulong),
        ("hwndCapture", c_ulong),
        ("hwndMenuOwner", c_ulong),
        ("hwndMoveSize", c_ulong),
        ("hwndCaret", c_ulong),
        ("rcCaret", RECT)
    ]


check = True
previos=-1
previoschar=''

def thread(my_func):
    def wrapper(*args, **kwargs):
        my_thread = threading.Thread(target=my_func, args=args, kwargs=kwargs)
        my_thread.start()
    return wrapper
def signal_handler(signal, frame):
    global interrupted
    interrupted = True    
def interrupt_callback():
    global interrupted
    return interrupted

stopf=0
stop2=0
model = Model("model")
rec = KaldiRecognizer(model, 16000)
p = pyaudio.PyAudio()

# Функция в которой решаем что отвечать на фразы пользователя (обработчик вопросов)  
def myvopros(data):
    ot=getanswer(data)
    return(ot)

def getpr(t):
    t=t.strip()
    t=t.replace('\n','. ')
    t=t.replace('\t','')
    t=t.replace('\r','. ')
    t=t.replace(';','. ')
    t=t.replace(',', '. ')
    t=t.replace(':', '. ')
    t=t.replace(' - ', '. ')
    t=t.replace('..','.')
    # Делим текст на массив предложений
    mas=re.split("\\b[.!?\\n]+(?=\\s)", t)
    return mas

@thread
def tick():
    global sluh
    global stoptime
    global oldtime
    while True:
        nowtime=int(time.time())
        razn=nowtime-oldtime
        if(razn>stoptime and sluh==1):
            sluh=0
            print('Лилия больше вас не слушает. Окликните её по имени, чтобы продолжить беседу.')
        time.sleep(1)

@thread
def say(mytext):
    global sluh
    global stop2
    global stopf
    global oldtime
    stop2=0
    stopf=1
    mastexts=getpr(mytext)
    for stroka in mastexts:
        if(len(stroka)>=2):
            synthesis_input = texttospeech.SynthesisInput(text=stroka)
            response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
            fname='mp3/'+re.sub('[^А-Яа-я]', '', stroka)+'.mp3'
            if not os.path.exists(fname):
                with open(fname, "wb") as out:
                    out.write(response.audio_content)
            mixer.music.load(fname)
            mixer.music.play()
            while mixer.music.get_busy() and stop2!=1:
                time.sleep(0.1)
            if(stop2==1):
                mixer.music.stop()
                stopf=0
                break
    stopf=0
    sluh=1
    oldtime=int(time.time())
    print('Сейчас Лилия слушает вас. можно не окликать ее по имени, а просто говорить вслух что-либо')
    

#mixer.stop()
#mixer.quit()  

@thread
def listencommand():
    global sluh
    global stop2
    print('Запущено распознавание с микрофона')
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()
    while True:
        if(stopf==0):
            data = stream.read(4000, exception_on_overflow=False)
            if len(data) == 0:
                continue
            if rec.AcceptWaveform(data):
                # Получили распознанную с микрофона фразу
                x=json.loads(rec.Result())["text"].lower()
                if len(x)>1:
                    print('Вы: '+x)

               
                # Если фраза начинается со слова Лилия то передаем сигнал в обработчик вопросов
                
                if (isbotname(x)!=None or sluh==1) and len(x)>1:
                    oldtime=int(time.time())
                    sluh=1
                    if(isbotname(x)!=None):
                        otv=myvopros(isbotname(x))
                    else:
                        otv=myvopros(x)
                    print('Лилия: '+otv)
                    say(otv+'.')
@thread
def getkeystop():
    global stop2
    while check:
        gti = GUITHREADINFO(cbSize=sizeof(GUITHREADINFO))
        user32.GetGUIThreadInfo(0, byref(gti))
        dwThread = user32.GetWindowThreadProcessId(gti.hwndActive, 0)
        lang = user32.GetKeyboardLayout(dwThread)
        if(lang==67699721):
            for x in range(1,255):
                if win32api.GetAsyncKeyState(ord(chr(x))):
                    # Нажатие на минус на цифровой панели останавливает синтез речи
                    # Работает только под Windows
                    if(x==109):
                        print(x)
                        stop2=1
                
tick()
getkeystop()
listencommand()
print('Чтобы активировать распознвание речи скажите фразу с именем "Лилия"')




