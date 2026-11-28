"""Owned UI translations; English keys and saved identifiers never change.

Native RNA uses the application's language. Custom drawing follows the add-on
language, or the application when Automatic is selected. Catalogs load only at
registration, not from a draw callback. Do not use this module for data names.
"""

from __future__ import annotations

import json
import logging
import re
import textwrap
import unicodedata
from pathlib import Path
from string import Formatter


# Owned native captions must not inherit an unrelated host translation.
# Native RNA descriptions still use Blender's default TIP context.
OWN_CONTEXT = "AnimAssist"
LANGUAGES = ("en", "ja", "ko", "zh", "pt", "es", "fr")
LANGUAGE_ITEMS = (
    ("AUTO", "Automatic", "Use the application interface language"),
    ("en", "English", "English"),
    ("ja", "日本語", "日本語"),
    ("ko", "한국어", "한국어"),
    ("zh", "简体中文", "简体中文"),
    ("pt", "Português", "Português"),
    ("es", "Español", "Español"),
    ("fr", "Français", "Français"),
)
LOCALE_ALIASES = {
    "ja": ("ja_JP", "ja"), "ko": ("ko_KR", "ko"),
    "zh": ("zh_HANS", "zh_CN", "zh_SG", "zh"),
    "pt": ("pt_BR", "pt_PT", "pt"), "es": ("es_ES", "es"),
    "fr": ("fr_FR", "fr"),
}
_ROOT = Path(__file__).resolve().parent
_REGISTRY_KEY = __package__ or __name__
_catalogs: dict[str, dict[str, str]] = {}
_registered = False
_log = logging.getLogger(__name__)


def normalize_language(locale: str) -> str:
    """Resolve supported locale aliases; do not call Traditional Chinese simplified."""
    value = str(locale or "").replace("-", "_").lower()
    if value in {"zh_tw", "zh_hant", "zh_hk"}:
        return "en"
    for language, aliases in LOCALE_ALIASES.items():
        if value in {alias.lower() for alias in aliases}:
            return language
    return "en"


def active_language(context=None) -> str:
    try:
        import bpy
        from ..prefs import get_prefs
        context = context or bpy.context
        prefs = get_prefs(context)
        choice = getattr(prefs, "language", "AUTO")
        if choice in LANGUAGES:
            return choice
        view = context.preferences.view
        if not getattr(view, "use_translate_interface", True):
            return "en"
        locale = getattr(view, "language", "DEFAULT")
        if locale == "DEFAULT":
            locale = bpy.app.translations.locale
        return normalize_language(locale)
    except (AttributeError, ImportError, KeyError, ReferenceError):
        return "en"


def T(english: str, *, language: str | None = None, context=None) -> str:
    """Translate a complete display string, never a persistent identifier."""
    if not english:
        return english
    language = language or active_language(context)
    return _catalogs.get(language, {}).get(english, english)


def native_text(english: str, msgctxt="*") -> str:
    """Use the host's language and context for host-owned RNA display metadata."""
    try:
        import bpy
        return bpy.app.translations.pgettext_iface(english, msgctxt)
    except (AttributeError, ImportError, ReferenceError):
        return english


def F(english: str, *args, language: str | None = None, **values) -> str:
    """Translate the template before formatting; leave inserted user data intact."""
    translated = T(english, language=language)
    try:
        return translated.format(*args, **values)
    except (KeyError, IndexError, ValueError, AttributeError):
        return english.format(*args, **values)


def error_text(error: Exception | str) -> str:
    """Render owned exception/reason templates before inserting literal data."""
    template = getattr(error, "ui_template", None)
    values = getattr(error, "ui_fields", None)
    if isinstance(template, str) and isinstance(values, dict):
        return F(template, **values)
    return T(str(error))


def placeholders(text: str) -> tuple[str, ...]:
    fields, state = [], {"automatic": False, "manual": False, "next": 0}

    def parse(value):
        normalized = ""
        for literal, field, spec, conversion in Formatter().parse(value):
            normalized += literal.replace("{", "{{").replace("}", "}}")
            if field is None:
                continue
            if field == "":
                state["automatic"] = True
                field = str(state["next"])
                state["next"] += 1
            elif field[0].isdigit():
                state["manual"] = True
            if state["automatic"] and state["manual"]:
                raise ValueError("Mixed automatic and manual format numbering")
            spec = parse(spec) if "{" in spec else spec
            signature = field + ("!" + conversion if conversion else "") + (":" + spec if spec else "")
            fields.append(signature)
            normalized += "{" + signature + "}"
        return normalized

    parse(text)
    return tuple(sorted(fields))


_PERCENT = re.compile(r"%(?:\(([^)]+)\))?([-+#0 ]*)(\d+|\*)?(\.(?:\d+|\*))?([diouxXeEfFgGcrsa%])")


def _percent_fields(text):
    positional, named = [], []
    escapes = 0
    position = 0
    while True:
        position = text.find("%", position)
        if position < 0:
            break
        match = _PERCENT.match(text, position)
        if match is None:
            raise ValueError("Invalid percent format")
        position = match.end()
        if match[5] == "%":
            if match.group(0) != "%%":
                raise ValueError("Invalid percent escape")
            escapes += 1
            continue
        signature = "".join(part or "" for part in match.groups()[1:])
        if match[1]:
            named.append((match[1], signature))
        else:
            positional.append(signature)
    return tuple(positional), tuple(sorted(named)), escapes


def validate_catalog(strings: dict[str, str], formats: dict[str, str] | None = None) -> list[str]:
    errors = []
    for source, target in strings.items():
        if not isinstance(source, str) or not isinstance(target, str) or not target:
            errors.append(f"Invalid translation: {source!r}")
            continue
        try:
            kind = formats.get(source, "literal") if formats is not None else "brace"
            invalid = kind == "brace" and placeholders(source) != placeholders(target)
            invalid = invalid or (kind == "percent" and _percent_fields(source) != _percent_fields(target))
            if invalid:
                errors.append(f"Placeholder mismatch: {source!r}")
        except ValueError:
            errors.append(f"Invalid format string: {source!r}")
    return errors


def wrap_text(text: str, width: int) -> list[str]:
    """Wrap help by display cells, retaining ordinary English word wrapping."""
    text = " ".join(text.split())
    width = max(2, int(width))
    if not any(unicodedata.east_asian_width(char) in {"W", "F"} for char in text):
        return textwrap.wrap(text, width=width)
    lines, line = [], ""

    def cells(value):
        return sum(0 if unicodedata.combining(char) else
                   2 if unicodedata.east_asian_width(char) in {"W", "F"} else 1 for char in value)

    for char in text:
        if line and cells(line + char) > width:
            split = line.rfind(" ")
            if split > 0:
                lines.append(line[:split].rstrip())
                line = line[split + 1:]
            else:
                lines.append(line)
                line = ""
        line += char
    if line.strip():
        lines.append(line.strip())
    return lines


def redraw(_self=None, context=None) -> None:
    """Refresh every home, without changing animation data or global preferences."""
    try:
        import bpy
        context = context or bpy.context
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                area.tag_redraw()
    except (AttributeError, ImportError, ReferenceError):
        pass


def register() -> None:
    global _registered
    if _registered:
        return
    import bpy
    _catalogs.clear()
    source_path = _ROOT / "source_catalog.json"
    entries = json.loads(source_path.read_text(encoding="utf-8")).get("entries", [])
    formats = {entry["msgid"]: entry.get("format", "literal") for entry in entries}
    for language in LOCALE_ALIASES:
        path = _ROOT / "catalogs" / (language + ".json")
        if not path.is_file():
            continue  # Infrastructure stage: completeness is checked before publication.
        strings = json.loads(path.read_text(encoding="utf-8"))
        errors = validate_catalog(strings, formats)
        if errors:
            raise ValueError("Invalid Anim Assist translation catalog: " + "; ".join(errors[:5]))
        _catalogs[language] = strings
    native = {}
    for language, strings in _catalogs.items():
        messages = {(context, entry["msgid"]): strings[entry["msgid"]]
                    for entry in entries if entry["msgid"] in strings
                    for context in entry["contexts"]}
        for locale in LOCALE_ALIASES[language]:
            native[locale] = messages
    bpy.app.translations.register(_REGISTRY_KEY, native)
    _registered = True


def unregister() -> None:
    global _registered
    if _registered:
        import bpy
        bpy.app.translations.unregister(_REGISTRY_KEY)
        _registered = False
    _catalogs.clear()
