import webbrowser
import pyttsx3
import requests
import musiclibrary
import pywhatkit
import re
from chat import get_answer

def processCommand(c):
    if c.lower() == "open google":
        pyttsx3.speak("Opening Google")
        webbrowser.open("https://google.com")
    elif c.lower() == "open youtube":
        pyttsx3.speak("Opening Youtube")
        webbrowser.open("https://youtube.com/")
    elif c.lower() == "open facebook":
        pyttsx3.speak("Opening facebook")
        webbrowser.open("https://facebook.com/")
    elif c.lower() == "open linkedin":
        pyttsx3.speak("Opening linkedin")
        webbrowser.open("https://linkedin.com/")
    elif c.lower() == "open netmirror":
        pyttsx3.speak("Opening netmirror")
        webbrowser.open("https://netmirror.app/1/en")
    elif "play" in c.lower() or "song" in c.lower():
        name = re.sub(r"\b(play|song|on youtube)\b", "", c, flags=re.IGNORECASE).strip()
        if name:
            pyttsx3.speak(f"Playing {name} on youtube")
            pywhatkit.playonyt(name)
        else:
            pyttsx3.speak("Please specify the song name.")
    elif "news" in c.lower():
        url = "https://newsapi.org/v2/top-headlines?country=us&apiKey=869c2995e40d4336a0f2dcd5cdcd009b"
        response = requests.get(url)
        data = response.json()
        articles = data.get("articles", [])
        if articles:
            pyttsx3.speak("Here are the top headlines:")
            for article in articles[:5]:  # Limit to top 5 headlines
                headline = article.get("title")
                if headline:
                    pyttsx3.speak(headline)
        else:
            pyttsx3.speak("Sorry, I couldn't fetch the news right now.")

    else:
        get_answer(c)

    


    # else: #"search" in c.lower() or "what is" in c.lower():
    #     query = c.lower().replace("search", "").strip() or c.lower().replace("what is", "").strip()
    #     if "search" in c.lower() or "what is" in c.lower():
    #         if query:
    #             pyttsx3.speak(f"Searching {query}")
    #         url = f"https://chatgpt.com/?q={query.replace(' ', '+')}"
    #         webbrowser.open(url)
    #         pyttsx3.speak("Here is what I found.")

    #     else:
    #         if "your name" in c.lower():
    #             reply = "My name is Jenny."
    #         elif "how are you" in c.lower():
    #             reply = "I'm doing great! How about you?"
    #         elif "hello" in c.lower() or "hi" in c.lower():
    #             reply = "Hello there! How can i help you ?"
    #         elif "what can you do" in c.lower():
    #             reply = "I can help you with various tasks like opening websites, playing music, fetching news, and answering questions."
    #         elif "what are you doing" in c.lower():
    #             reply = "nothing!, apna kaam kar rahi hoon"
    #         else:
    #             reply = "I'm Jenny, your assistant, but I don't know that yet."

    #         print(f"Jenny: {reply}")
    #         pyttsx3.speak(reply)

