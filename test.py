import gtts
from gtts.tts import gTTSError
from playsound import playsound

tts = gtts.gTTS("halv två", lang="sv")

try:
    tts.save("test.mp3")
except gTTSError as e:
    print(e)

playsound("test.mp3")