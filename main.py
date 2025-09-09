import speech_recognition as sr
import pyttsx3  
from process_command import processCommand



newapi = "869c2995e40d4336a0f2dcd5cdcd009b"



if __name__ == "__main__":
    pyttsx3.speak("initializing jenny")

    while True:
        # obtain audio from the microphone
        r = sr.Recognizer()
        print("Initializing jenny")

        # recognize speech using Sphinx
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = r.listen(source, timeout=5) 
            word = r.recognize_google(audio)
            print(word)
            if word.lower() == "jenny":
                pyttsx3.speak("hmmmmm hmmmmm")
                with sr.Microphone() as source:
                    print("Listening...")
                    audio = r.listen(source, timeout=5) 
                    command = r.recognize_google(audio)
                    print("Command: ",command)
                    if command.lower() == "exit":
                        pyttsx3.speak("exiting software")
                        pyttsx3.speak("Goodbye! Have a great day!")
                        break
                    else:
                        response = processCommand(command)
                        print("Jenny: ",response)
            elif word.lower() == "exit":
                pyttsx3.speak("exiting software")
                pyttsx3.speak("Goodbye! Have a great day!")
                break



        except Exception as e:
            print("Error; {0}".format(e))
