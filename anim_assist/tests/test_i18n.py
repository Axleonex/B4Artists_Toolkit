"""Pure-Python checks for the owned translation boundary (no Blender required)."""

import importlib.util
import json
import pathlib
import sys
import tempfile
import types
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
PACKAGE = "aa_i18n_adapter_tests"
package = types.ModuleType(PACKAGE)
package.__path__ = [str(ROOT)]
sys.modules[PACKAGE] = package
SPEC = importlib.util.spec_from_file_location(PACKAGE + ".i18n", ROOT / "i18n" / "__init__.py")
i18n = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(i18n)


class TranslationTests(unittest.TestCase):
    def tearDown(self):
        i18n.unregister()

    def test_locale_aliases(self):
        for source, expected in (("ja_JP", "ja"), ("ko_KR", "ko"),
                                 ("zh_HANS", "zh"), ("zh_CN", "zh"),
                                 ("pt_BR", "pt"), ("pt_PT", "pt"),
                                 ("es_ES", "es"), ("fr_FR", "fr"),
                                 ("en_US", "en"), ("xx", "en")):
            self.assertEqual(i18n.normalize_language(source), expected)

    def test_unknown_and_technical_values_are_unchanged(self):
        self.assertEqual(i18n.T("Pose.L"), "Pose.L")
        self.assertEqual(i18n.T(""), "")

    def test_templates_preserve_data_and_allow_reordering(self):
        i18n._catalogs["fr"] = {"Select {name}: {count:d}": "{count:d} : sélectionnez {name}"}
        self.assertEqual(i18n.F("Select {name}: {count:d}", language="fr", name="Bone.L", count=3),
                         "3 : sélectionnez Bone.L")

    def test_invalid_template_translation_falls_back_to_source(self):
        i18n._catalogs["ja"] = {"Select {name}": "{other}"}
        self.assertEqual(i18n.F("Select {name}", language="ja", name="Bone.L"), "Select Bone.L")

    def test_live_language_change_uses_same_english_key(self):
        i18n._catalogs.update(fr={"Settings": "Réglages"}, ja={"Settings": "設定"})
        self.assertEqual(i18n.T("Settings", language="fr"), "Réglages")
        self.assertEqual(i18n.T("Settings", language="ja"), "設定")
        self.assertEqual(i18n.T("Settings", language="en"), "Settings")

    def test_placeholder_validation(self):
        self.assertEqual(i18n.validate_catalog({"Move {name} by {value:.2f}": "{value:.2f} {name}"}), [])
        self.assertTrue(i18n.validate_catalog({"Move {name}": "Déplacer {other}"}))
        self.assertTrue(i18n.validate_catalog({"Move {name}": ""}))

    def test_format_numbering_and_percent_order(self):
        self.assertEqual(i18n.validate_catalog({"{}: {:d}": "{0}: {1:d}"}), [])
        self.assertTrue(i18n.validate_catalog({"{}: {:d}": "{}: {1:d}"}))
        self.assertTrue(i18n.validate_catalog({"Name %s: %d": "Nom %d : %s"}, {"Name %s: %d": "percent"}))
        self.assertEqual(i18n.validate_catalog({"%(name)s: %(count)d": "%(count)d : %(name)s"}, {"%(name)s: %(count)d": "percent"}), [])
        self.assertEqual(i18n.validate_catalog({"50% of keys": "50% des clés"}), [])
        self.assertEqual(i18n.validate_catalog({"50% of keys": "50 % des clés"}), [])

    def test_automatic_language_follows_live_application_state(self):
        context = types.SimpleNamespace(
            preferences=types.SimpleNamespace(view=types.SimpleNamespace(language="fr_FR", use_translate_interface=True)),
            addon_prefs=types.SimpleNamespace(language="AUTO"))
        fake_bpy = types.SimpleNamespace(context=context, app=types.SimpleNamespace(
            translations=types.SimpleNamespace(locale="zh_HANS")))
        prefs_name = PACKAGE + ".prefs"
        previous_bpy, previous_prefs = sys.modules.get("bpy"), sys.modules.get(prefs_name)
        sys.modules["bpy"] = fake_bpy
        sys.modules[prefs_name] = types.SimpleNamespace(get_prefs=lambda ctx: ctx.addon_prefs)
        try:
            self.assertEqual(i18n.active_language(context), "fr")
            context.preferences.view.language = "ja_JP"
            self.assertEqual(i18n.active_language(context), "ja")
            context.preferences.view.use_translate_interface = False
            self.assertEqual(i18n.active_language(context), "en")
            context.addon_prefs.language = "ko"
            self.assertEqual(i18n.active_language(context), "ko")
            context.addon_prefs.language = "AUTO"
            context.preferences.view.use_translate_interface = True
            context.preferences.view.language = "DEFAULT"
            self.assertEqual(i18n.active_language(context), "zh")
        finally:
            for key, previous in (("bpy", previous_bpy), (prefs_name, previous_prefs)):
                if previous is None:
                    sys.modules.pop(key, None)
                else:
                    sys.modules[key] = previous

    def test_cjk_wrapping_uses_display_cells(self):
        self.assertEqual(i18n.wrap_text("选择动画关键帧", 8), ["选择动画", "关键帧"])
        self.assertEqual(i18n.wrap_text("Select the animated object", 12), ["Select the", "animated", "object"])

    def test_literal_prose_does_not_infer_executable_percent_fields(self):
        prose = {"100% effect": "100 % d’effet", "100% of selected keys": "100 % des clés sélectionnées"}
        self.assertEqual(i18n.validate_catalog(prose, {key: "literal" for key in prose}), [])
        self.assertTrue(i18n.validate_catalog({"Name %s: %d": "Nom %d : %s"}, {"Name %s: %d": "percent"}))
        self.assertTrue(i18n.validate_catalog({"Count {count:d}": "Nombre {other:d}"}, {"Count {count:d}": "brace"}))
        self.assertTrue(i18n.validate_catalog({"Frame 1 %s": "Cadre 1"}, {"Frame 1 %s": "percent"}))
        self.assertTrue(i18n.validate_catalog({"Version 2 %s": "Version 2 %d"}, {"Version 2 %s": "percent"}))
        self.assertTrue(i18n.validate_catalog({"Amount %d%%": "Montant %d %"}, {"Amount %d%%": "percent"}))
        self.assertEqual(i18n.validate_catalog({"Amount %d%%": "Montant %d%%"}, {"Amount %d%%": "percent"}), [])

    def test_host_metadata_uses_its_actual_translation_context(self):
        calls = []
        fake = types.SimpleNamespace(app=types.SimpleNamespace(translations=types.SimpleNamespace(
            pgettext_iface=lambda source, context: calls.append((source, context)) or "スクリプト式")))
        previous = sys.modules.get("bpy")
        sys.modules["bpy"] = fake
        try:
            self.assertEqual(i18n.native_text("Scripted Expression", "Driver"), "スクリプト式")
            self.assertEqual(calls, [("Scripted Expression", "Driver")])
        finally:
            if previous is None:
                sys.modules.pop("bpy", None)
            else:
                sys.modules["bpy"] = previous

    def test_decorated_percent_escapes_are_invalid(self):
        source = "Amount %d%%"
        for target in ("Montant %d%5%", "Montant %d%-5%", "Montant %d%.2%", "Montant %d%(key)%", "Montant %d"):
            with self.subTest(target=target):
                self.assertTrue(i18n.validate_catalog({source: target}, {source: "percent"}))
        self.assertEqual(i18n.validate_catalog({source: "Montant %d%%"}, {source: "percent"}), [])

    def test_native_registration_and_cleanup_are_symmetric(self):
        calls = []
        translations = types.SimpleNamespace(
            register=lambda key, data: calls.append(("register", key, data)),
            unregister=lambda key: calls.append(("unregister", key)),
        )
        fake = types.SimpleNamespace(app=types.SimpleNamespace(translations=translations))
        previous = sys.modules.get("bpy")
        sys.modules["bpy"] = fake
        old_root = i18n._ROOT
        try:
            with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
                i18n._ROOT = pathlib.Path(directory)
                (i18n._ROOT / "catalogs").mkdir()
                source = {"entries": [{"msgid": "Settings", "contexts": ["*"]},
                                      {"msgid": "Bake", "contexts": ["Operator"]}]}
                (i18n._ROOT / "source_catalog.json").write_text(json.dumps(source), encoding="utf-8")
                for language in i18n.LOCALE_ALIASES:
                    (i18n._ROOT / "catalogs" / (language + ".json")).write_text(
                        json.dumps({"Settings": "設定", "Bake": "ベイク"}), encoding="utf-8")
                i18n.register()
                self.assertEqual(calls[0][0], "register")
                payload = calls[0][2]
                for language, aliases in i18n.LOCALE_ALIASES.items():
                    for alias in aliases:
                        self.assertEqual(payload[alias]["*", "Settings"], "設定")
                        self.assertEqual(payload[alias]["Operator", "Bake"], "ベイク")
                        self.assertNotIn(("Operator", "Settings"), payload[alias])
                i18n.unregister()
                self.assertEqual(calls[-1][:2], ("unregister", i18n._REGISTRY_KEY))
                i18n.unregister()
                self.assertEqual(sum(call[0] == "unregister" for call in calls), 1)
        finally:
            i18n._ROOT = old_root
            if previous is None:
                sys.modules.pop("bpy", None)
            else:
                sys.modules["bpy"] = previous


if __name__ == "__main__":
    unittest.main()
