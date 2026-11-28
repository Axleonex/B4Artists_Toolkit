# Anim Assist translations

English source text is the key. Keep identifiers, user names, paths, enum values,
and saved settings unchanged.

Add translations to `catalogs/ja.json`, `ko.json`, `zh.json`, `pt.json`, `es.json`,
and `fr.json`. Each file is one JSON object: English source text to translated text.
Use Simplified Chinese and Brazilian Portuguese. Do not add incomplete example catalogs.

Run `python anim_assist/i18n/extract.py` after source changes. This offline command
writes `source_catalog.json`. Run it with `--check` to detect a stale catalog.
The catalog records each source path, line, display kind, and actual native context.
An empty `contexts` list means the text is used only by our custom display code.
Native operator labels use `Operator`; native descriptions use `*`. Owned operator
help uses our callback. The saved-layout enum has an empty native namespace so
Blender does not translate a user's layout name.
Enum contexts come from the actual property consumer, including imported callback
functions. A table name alone does not assign a native translation context.
Class-local enum aliases retain their owning scope. Imported callbacks use their
own module bindings.

`native_dependencies.json` lists only host RNA fields used by these tools. It
records their real RNA identifiers, original contexts, and native survey evidence.
The extractor merges these into `native_sources`; it does not invent source files
for host strings. Modifier names use the host's `Action` context. Handle names and
native descriptions use `*`. The host catalog takes precedence over our fallback
translations. Native enum identifiers remain unchanged.

The optional `format` field is `brace` or `percent` only when source code executes
that format. If the field is absent, treat the text as literal prose. Preserve all
format fields and conversion types. Percentage signs in prose are ordinary text.
The extractor rejects conflicting executable format types for one source key.

The add-on language setting controls custom labels, helpers, reports, and overlays.
`Automatic` follows the application interface language. If interface translation
is off, `Automatic` uses English. Native controls follow the application language.
For a complete translated interface, select the same language in both settings.
Language changes redraw the interface without registering the add-on classes again.

Use `T` for complete fixed captions. Use `F` for a complete format template before
inserting data. Translate owned captions before measuring or composing them. Set
`translate=False` on native layout text that is already translated or contains user
data. Use `native_text` with the original RNA context for host-owned enum captions.
Never translate an identifier or write to the application's language preferences.
Owned dynamic description callbacks return complete display text. Do not pass that
output through `T` again. Static fallback help is translated when it is selected.
Use `error_text` for exceptions from the toolbar model; it retains field values.
The discovery registry stores original English operator metadata. Search checks
both that text and its current translation. Discovery enum callbacks translate on
access and include the language in their cache key. Their native namespace,
`AnimAssist.ToolChoices`, stays empty to protect the completed display text.
