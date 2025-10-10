import webbrowser
import requests
import musiclibrary
import re
from chat import get_answer
import random
try:
    import pywhatkit
except Exception:
    pywhatkit = None
    print("pywhatkit disabled (no display environment available)")


def processCommand(c: str) -> str:
    """Process user command and return text for display."""

    user_greetings = ["hey", "hii", "hello", "hello there!", "hi", "heyy", "hola", "yo"]
    bot_replies = [
        "Hey there! How's it going?",
        "Hello! Nice to see you 😃",
        "Hi It's Jenny! What's up?",
        "Hey I'm Jenny! How are you doing today?",
        "Hii, hope you're having a great day!",
        "Hello there, friend!",
        "Yo! Glad you're here 😎",
        "Hey hey! How’s everything?",
        "Hello! How can I assist you today?",
    ]
    word = ["jenny"]
    replyy = ["hmmmmm hmmmmm", "yes?", "how can I help you?", "at your service", "what's up?"]

    c_low = c.lower().strip()

    if c_low == "open google":
        webbrowser.open("https://google.com")
        return "Opening Google"

    elif c_low == "open youtube":
        webbrowser.open("https://youtube.com/")
        return "Opening YouTube"

    elif c_low == "open facebook":
        webbrowser.open("https://facebook.com/")
        return "Opening Facebook"

    elif c_low == "open linkedin":
        webbrowser.open("https://linkedin.com/")
        return "Opening LinkedIn"

    elif c_low == "open netmirror":
        webbrowser.open("https://netmirror.app/1/en")
        return "Opening Netmirror"

    # --- Greetings ---
    elif c_low in word:
        return random.choice(replyy)

    elif c_low in [g.lower() for g in user_greetings]:
        return random.choice(bot_replies)

    elif "play" in c_low or "song" in c_low:
        name = re.sub(r"\b(play|song|on youtube)\b", "", c, flags=re.IGNORECASE).strip()
        if name:
            if pywhatkit:  # Only run if pywhatkit successfully imported
                try:
                    pywhatkit.playonyt(name)
                    return f"Playing {name} on YouTube"
                except Exception as e:
                    print(f"pywhatkit failed: {e}")
                    return f"Unable to play '{name}' on YouTube (unsupported environment)."
            else:
                return f"Cannot play '{name}' on YouTube — this feature is unavailable on Render."
        else:
            return "Please specify the song name."


    elif "news" in c_low:
        url = "https://newsapi.org/v2/top-headlines?country=us&apiKey=869c2995e40d4336a0f2dcd5cdcd009b"
        try:
            response = requests.get(url)
            data = response.json()
            articles = data.get("articles", [])
            if articles:
                headlines = [article.get("title") for article in articles[:5] if article.get("title")]
                return "Top headlines:\n" + "\n".join(headlines)
            else:
                return "Sorry, I couldn't fetch the news right now."
        except Exception:
            return "Error while fetching news."

    else:
        reply = get_answer(c)
        return reply if reply else "Sorry, I didn’t understand that."
