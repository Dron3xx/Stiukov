import re
from pathlib import Path

import language_tool_python
import regex

tool = language_tool_python.LanguageTool("en-US")
project_dir = Path(__file__).parent.parent

IGNORE_RULES = {
    "WHITESPACE_RULE",
    "CONSECUTIVE_SPACES",
    "COMMA_PARENTHESIS_WHITESPACE",
    "UPPERCASE_SENTENCE_START",
    "EN_COMPOUNDS_CASE_INSENSITIVE",
    "EN_COMPOUNDS_LONG_LIVED",
    "EN_COMPOUNDS_NON_EMPTY",
    "YOUTUBE",
}

IGNORE_WORDS = {
    "stiukov",
    "stiukov.py",
    "apps_search.py",
    "apps_search",
    "pyttsx3",
    "pyautogui",
    "pyperclip",
    "psutil",
    "pycaw",
    "ctypes",
    "opencv",
    "numpy",
    "pillow",
    "tensorflow",
    "speechrecognition",
    "win32api",
    "windows",
    "youtube",
    "json",
    "notepad.exe",
    "saved_words.txt",
    "greetings.json",
    "jokes.json",
    "applications.json",
    "version.dll",
    "record_audio",
    "speak",
    "respond",
    "handle_greeting",
    "handle_application",
    "handle_joke",
    "handle_web_command",
    "handle_volume",
    "search_applications",
    "search_registry_apps",
    "search_disk",
    "read_file_metadata",
    "os.startfile",
    "win32api",
    "FileDescription",
    "search disk()"
}


def markdown_to_plain_text(md_text: str) -> str:
    md_text = re.sub(r"```.*?```", "\n", md_text, flags=re.S)
    md_text = re.sub(r"!\[.*?\]\(.*?\)", "", md_text)
    md_text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", md_text)
    md_text = re.sub(r"`([^`]+)`", r"\1", md_text)
    md_text = re.sub(r"[*_>#-]+", " ", md_text)
    md_text = re.sub(r"[ \t]+", " ", md_text)
    md_text = re.sub(r"\n{3,}", "\n\n", md_text)
    return md_text.strip()


def normalize_line_for_check(line: str) -> str:

    cleaned = re.sub(r"```.*?```", " ", line, flags=re.S)
    cleaned = re.sub(r"!\[.*?\]\(.*?\)", "", cleaned)
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cleaned)
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    cleaned = re.sub(r"\b[A-Za-z_][A-Za-z0-9_]*\s*\([^)]*\)", " ", cleaned)
    cleaned = re.sub(r"\b[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z0-9_\.]+", " ", cleaned)
    cleaned = re.sub(r"\b[A-Za-z_][A-Za-z0-9_]*\s*=\s*[^\n]+", " ", cleaned)
    cleaned = re.sub(r"[\*_>#-]+", " ", cleaned)
    cleaned = re.sub(r",\s*,", ",", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)

    return cleaned.strip()


def should_ignore_match(text: str, match) -> bool:
    if match.rule_id in IGNORE_RULES:
        return True

    start = max(match.offset, 0)
    end = min(match.offset + match.error_length, len(text))
    word = text[start:end].strip().lower()

    if not word:
        return True

    normalized = word.strip("`'\"()[]{}.,:;!?")
    if normalized in IGNORE_WORDS:
        return True

    if any(token in normalized for token in (
        "stiukov", "py", "psutil", "pycaw", "opencv",
        "numpy", "tensorflow", "apps", "handle_",
        "search_", "record_", "read_", "json", "dll",
        "startfile", "win32api", "filedescription", "ctypes"
        )):
        return True

    return False


def should_ignore_word(word):
    return word.lower() in IGNORE_WORDS


def check_md_grammar():
    results = {}
    for md_path in project_dir.rglob("*.md"):
        if ".pytest_cache" in md_path.parts:
            continue

        lines = md_path.read_text(encoding="utf-8").splitlines()
        grammar_issues  = []
        suspicious_word_issues = []
        in_code_block = False

        for line_number, raw_line in enumerate(lines, start=1):
            stripped = raw_line.strip()

            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue

            if in_code_block:
                continue

            cleaned_line = normalize_line_for_check(raw_line)
            if not cleaned_line:
                continue
            for match in tool.check(cleaned_line):
                if should_ignore_match(cleaned_line, match):
                    continue
                grammar_issues.append({
                    "line": line_number,
                    "match": match,
                    "source": raw_line.strip(),
                    "plain": cleaned_line,
                })

            for word in regex.findall(
                r"\b(?=[A-Za-z0-9]*[A-Za-z])(?=[A-Za-z0-9]*\d)[A-Za-z0-9]+\b",
                cleaned_line):
                if should_ignore_word(word):
                    continue
                suspicious_word_issues.append({
                    "line": line_number,
                    "word": word,
                    "source": raw_line.strip(),
                })

        results[str(md_path)] = {
            "grammar": grammar_issues,
            "suspicious_words": suspicious_word_issues,
        }

    return results

def test_documentation_grammar():
    issues = check_md_grammar()

    for path, results in issues.items():
        grammar_issues = results["grammar"]
        suspicious_word_issues = results["suspicious_words"]
        print("Grammar:", path, len(grammar_issues))
        for item in grammar_issues:
            match = item["match"]
            print(f" - Line {item['line']}: {match.rule_id} | {match.message}")
            print(f"   Source: {item['source'][:160]}")
            print(f"   Context: {match.context}")

        assert not grammar_issues


        print("Suspicious words:", path, len(suspicious_word_issues))
        for item in suspicious_word_issues:
            print(f" - Line {item['line']}: Suspicious word with digit | {item['word']}")
            print(f"   Source: {item['source'][:160]}")

        assert not suspicious_word_issues

