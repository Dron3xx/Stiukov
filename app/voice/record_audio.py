import speech_recognition as sr


recognizer = sr.Recognizer()

def record_audio(ask=False):
    voice_data = ''
    with sr.Microphone() as source:
        if ask:
            print(ask)
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            print("Recognizing...")
            voice_data = recognizer.recognize_google(audio, language='en-EN')
            print(f"Recognized: {voice_data.lower()}")
        except sr.UnknownValueError:
            print('Speech not recognized')
        except sr.RequestError as e:
            print(f'Could not request results; {e}')
    return voice_data.lower()