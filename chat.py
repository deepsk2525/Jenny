import sys
import time
import traceback
from typing import List, Tuple

# --- Web Search & Scrape ---
from duckduckgo_search import DDGS
import trafilatura

# --- Chat model (no OpenAI key) ---
import g4f

# =========================
# Utilities
# =========================

def web_search(query: str, max_results: int = 6) -> List[Tuple[str, str]]:
    """Search the web and return [(title, url), ...]."""
    out = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            title = (r.get("title") or "").strip()
            url = (
                r.get("href")
                or r.get("url")
                or r.get("link")
                or ""
            ).strip()
            if title and url:
                out.append((title, url))
    return out

def fetch_and_extract(url: str, timeout: int = 15) -> str:
    """Fetch URL and extract clean article text with trafilatura."""
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

def summarize_with_gpt(query: str, docs: List[Tuple[str, str, str]], max_chars: int = 6000) -> str:
    """Summarize using g4f (no OpenAI key). Truncates long inputs."""
    parts, used = [], 0
    for title, url, text in docs:
        if not text:
            continue
        chunk = f"SOURCE: {title}\nURL: {url}\n{text}\n"
        need = len(chunk)
        if used + need > max_chars:
            chunk = chunk[: max(0, max_chars - used)]
        parts.append(chunk)
        used += len(chunk)
        if used >= max_chars:
            break

    context = "".join(parts) if parts else "No content extracted."

    system_prompt = (
        "You are Jenny, a concise research assistant. "
        "Always reply in **under 80 words**, clear and direct. "
        "If uncertain, say so briefly. "
        "Cite sources inline like [1], [2]."
    )

    numbered = [f"[{i}] {title} — {url}" for i, (title, url, text) in enumerate(docs, start=1)]
    src_list = "\n".join(numbered) if numbered else "[1] No sources"

    prompt = (
        f"User Query:\n{query}\n\n"
        f"Sources:\n{src_list}\n\n"
        f"Extracted:\n{context}\n\n"
        f"Task: Provide a short, accurate answer under 80 words."
    )

    try:
        resp = g4f.ChatCompletion.create(
            model=g4f.models.default,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        return (resp or "").strip()
    except Exception as e:
        return f"(Model error) {e}"

def choose_sources(results: List[Tuple[str, str]], limit: int = 3) -> List[Tuple[str, str]]:
    return results[:limit]

# =========================
# Main Jenny loop
# =========================

def run_Jenny():
    print("🤖 Internet-powered Chat Jenny (no OpenAI key)")
    print("Type your question. Commands: 'exit' to quit.\n")

    while True:
        try:
            query = input("You: ").strip()
            if not query:
                continue
            if query.lower() in {"exit", "quit", "bye"}:
                print("Jenny: Goodbye!")
                break

            print("🔍 Searching the web...")
            results = web_search(query, max_results=8)
            if not results:
                print("Jenny: I couldn't find results for that right now.")
                continue

            picks = choose_sources(results, limit=3)
            docs = [(title, url, fetch_and_extract(url)) for title, url in picks]

            print("🧠 Summarizing with ChatGPT (g4f)...")
            answer = summarize_with_gpt(query, docs)

            print("\n===== Answer =====")
            print(answer)
            print("\n===== Sources =====")
            for i, (title, url, _text) in enumerate(docs, start=1):
                print(f"[{i}] {title} — {url}")

        except KeyboardInterrupt:
            print("\nJenny: Stopped.")
            break
        except Exception as e:
            print("⚠️ Error:", e)
            traceback.print_exc()

def get_answer(query: str) -> str:
    try:
        print(f"🔍 Searching the web for: {query}")
        results = web_search(query, max_results=8)
        if not results:
            return "No results found."

        picks = choose_sources(results, limit=3)
        docs = [(title, url, fetch_and_extract(url)) for title, url in picks]

        print("🧠 Summarizing with ChatGPT (g4f)...")
        answer = summarize_with_gpt(query, docs)

        print("\n===== Jenny's Answer =====")
        print(answer)
        return answer
    except Exception as e:
        print("⚠️ Error:", e)
        return "Sorry, something went wrong."
