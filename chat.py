import sys
import time
import traceback
from typing import List, Tuple

# --- Web Search & Scrape ---
from duckduckgo_search import DDGS
import trafilatura

# --- Voice (optional) & TTS ---
import pyttsx3
try:
    import speech_recognition as sr
    HAS_SR = True
except Exception:
    HAS_SR = False

# --- Chat model (no OpenAI key) ---
import g4f

# =========================
# Utilities
# =========================


def speak(text: str, rate: int = 175):
    engine = pyttsx3.init()
    engine.setProperty("rate", rate)
    engine.say(text)
    engine.runAndWait()

def listen(language: str = "en-IN") -> str:
    """Voice input. Requires SpeechRecognition + pyaudio."""
    if not HAS_SR:
        print("🎤 SpeechRecognition not installed; falling back to text input.")
        return input("You: ").strip()

    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        r.pause_threshold = 0.8
        r.energy_threshold = 250
        audio = r.listen(source, timeout=5, phrase_time_limit=15)
    try:
        print("🔎 Recognizing...")
        query = r.recognize_google(audio, language=language)
        print(f"You: {query}")
        return query.strip()
    except Exception:
        print("⚠️ Didn't catch that. Type instead:")
        return input("You: ").strip()

def web_search(query: str, max_results: int = 6) -> List[Tuple[str, str]]:
    """
    Search the web and return [(title, url), ...].
    Uses DuckDuckGo for reliability (no API key).
    """
    out = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            title = (r.get("title") or "").strip()
            url = (r.get("href") or r.get("url") or "").strip()
            if title and url:
                out.append((title, url))
    return out

def fetch_and_extract(url: str, timeout: int = 15) -> str:
    """
    Fetch URL and extract clean article text with trafilatura.
    """
    try:
        downloaded = trafilatura.fetch_url(url, timeout=timeout)
        if not downloaded:
            return ""
        extracted = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=False,
            no_fallback=False,
            include_images=False,
            favor_precision=True,
        )
        return (extracted or "").strip()
    except Exception:
        return ""

def summarize_with_gpt(query: str, docs: List[Tuple[str, str, str]], max_chars: int = 9000) -> str:
    """
    Summarize using g4f (no OpenAI key). Truncates long inputs.
    `docs` = list of (title, url, text)
    """
    # Build a compact context
    parts = []
    used = 0
    for title, url, text in docs:
        if not text:
            continue
        chunk = f"\n\nSOURCE: {title}\nURL: {url}\nCONTENT:\n{text}\n"
        need = len(chunk)
        if used + need > max_chars:
            chunk = chunk[: max(0, max_chars - used)]
        parts.append(chunk)
        used += len(chunk)
        if used >= max_chars:
            break

    context = "".join(parts) if parts else "No content extracted."

    system_prompt = (
        "You are a concise web research Jenny. "
        "Answer the user's query using only the provided sources. "
        "Cite sources inline as [#] using the numeric order they are presented. "
        "If uncertain, say so briefly."
    )

    # Build numbered source map for inline citations
    numbered = []
    for i, (title, url, text) in enumerate(docs, start=1):
        tag = f"[{i}] {title} — {url}"
        numbered.append(tag)
    src_list = "\n".join(numbered) if numbered else "[1] No sources"

    prompt = (
        f"User Query:\n{query}\n\n"
        f"Sources (numbered):\n{src_list}\n\n"
        f"Extracted Content:\n{context}\n\n"
        f"Task: Provide a helpful answer in under 200 words, with inline citations like [1], [2]."
    )

    # Call g4f
    try:
        resp = g4f.ChatCompletion.create(
            model=g4f.models.default,  # auto-selects a free provider/model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            # You can set stream=False/True depending on provider; keeping default for simplicity
        )
        return (resp or "").strip()
    except Exception as e:
        return f"(Model error) {e}"

def choose_sources(results: List[Tuple[str, str]], limit: int = 3) -> List[Tuple[str, str]]:
    """Pick a few top results; you can add filtering rules here."""
    return results[:limit]

# =========================
# Main Jenny loop
# =========================

def run_Jenny(voice_mode: bool = False, speak_back: bool = True):
    print("🤖 Internet-powered Chat Jenny (no OpenAI key)")
    print("Type your question, or say it (if voice_mode=True).")
    print("Commands: 'exit' to quit.\n")

    while True:
        try:
            query = listen() if voice_mode else input("You: ").strip()
            if not query:
                continue
            if query.lower() in {"exit", "quit", "bye"}:
                print("Jenny: Goodbye!")
                if speak_back:
                    speak("Goodbye!")
                break

            print("🔍 Searching the web...")
            results = web_search(query, max_results=8)
            if not results:
                answer = "I couldn't find results for that right now."
                print(f"Jenny: {answer}")
                if speak_back:
                    speak(answer)
                continue

            picks = choose_sources(results, limit=3)
            docs = []
            print("📥 Fetching pages...")
            for title, url in picks:
                text = fetch_and_extract(url)
                docs.append((title, url, text))

            print("🧠 Summarizing with ChatGPT (g4f)...")
            answer = summarize_with_gpt(query, docs)

            # Show sources + answer
            print("\n===== Answer =====")
            print(answer)
            print("\n===== Sources =====")
            for i, (title, url, _text) in enumerate(docs, start=1):
                print(f"[{i}] {title} — {url}")

            if speak_back:
                # Speak a shorter version to avoid droning
                to_say = answer
                if len(to_say) > 600:
                    to_say = to_say[:600] + "…"
                speak(to_say)

        except KeyboardInterrupt:
            print("\nJenny: Stopped.")
            break
        except Exception as e:
            print("⚠️ Error:", e)
            traceback.print_exc()
            if speak_back:
                speak("Sorry, I hit an error.")



# Existing imports remain same

def get_answer(query: str, speak_back: bool = True) -> str:
    """Takes a command, searches the web, summarizes, and returns the answer."""
    try:
        print(f"🔍 Searching the web for: {query}")
        results = web_search(query, max_results=8)
        if not results:
            answer = "I couldn't find results for that right now."
            if speak_back:
                speak(answer)
            return answer

        picks = choose_sources(results, limit=3)
        docs = []
        print("📥 Fetching pages...")
        for title, url in picks:
            text = fetch_and_extract(url)
            docs.append((title, url, text))

        print("🧠 Summarizing with ChatGPT (g4f)...")
        answer = summarize_with_gpt(query, docs)

        # Show answer
        print("\n===== Answer =====")
        print(answer)
        print("\n===== Sources =====")
        for i, (title, url, _text) in enumerate(docs, start=1):
            print(f"[{i}] {title} — {url}")

        if speak_back:
            to_say = answer
            if len(to_say) > 600:
                to_say = to_say[:600] + "…"
            speak(to_say)

        return answer
    except Exception as e:
        print("⚠️ Error:", e)
        if speak_back:
            speak("Sorry, I hit an error.")
        return "Sorry, something went wrong."

# if __name__ == "__main__":
#     # Toggle these flags as you like:
#     run_Jenny(voice_mode=False, speak_back=True)
