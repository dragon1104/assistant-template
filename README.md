# assistant-template
Шаблон голосового ассистента (под Python 3.8.2)

Поставьте https://visualstudio.microsoft.com/ru/thank-you-downloading-visual-studio/?sku=Community&rel=16 в установщике отметьте Python и C++

Установите whl файл PyAudio отсюда https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

Установите следующие библиотеки:

pip install python-Levenshtein
pip install fuzzywuzzy
pip install pypiwin32
pip install vosk
pip install requests
pip install keyboard
pip install pygame

Если какой-то библиотеки будет не хватать - установите её тоже

Зарегистрируйтесь в https://cloud.google.com/text-to-speech и получите JSON файл для доступа к Google TTS (Инструкция тут - https://cloud.google.com/text-to-speech/docs/quickstart-protocol)

Поместите файл JSON в папку с программой и измените его имя внутри кода программы




