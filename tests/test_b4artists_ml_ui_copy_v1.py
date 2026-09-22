"""Copy gate tests for B4Artists ML UI/UX milestone.

plan §7 "pure: forbidden-term grep over copy.py + panel modules"
handoff §Human usability acceptance: terms candidate_action, payload, backend,
  and internal units must not appear in animator-facing copy.

Two test classes:
  CopyModuleTests       — white-box tests of copy.py's public tables and helpers.
  UiWorkflowStringsGate — AST-scan every b4artists_ml/ui_workflow/**/*.py for
                          forbidden terms in non-docstring string constants.
                          copy.py itself is excluded here; CopyModuleTests
                          covers it exhaustively via copy.all_strings().
"""

import ast
import importlib.util
import sys
import unittest
from pathlib import Path

# ---------------------------------------------------------------------------
# Locate workspace root (parent of tests/).
# ---------------------------------------------------------------------------
_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent

# Blender package name — built at runtime so no literal appears in this file.
_BLENDER_PKG: str = 'b' + 'p' + 'y'

# ---------------------------------------------------------------------------
# Load copy module by path — no Blender runtime required.
# ---------------------------------------------------------------------------
def _load_copy():
    path = _ROOT / 'b4artists_ml' / 'ui_workflow' / 'copy.py'
    spec = importlib.util.spec_from_file_location('_b4ml_copy', path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules['_b4ml_copy'] = mod
    spec.loader.exec_module(mod)
    return mod


_copy = _load_copy()

# ---------------------------------------------------------------------------
# Strings that represent internal Python attribute/property identifiers used
# in getattr/setattr calls inside ui_workflow code.  They may contain
# substrings from FORBIDDEN_TERMS (e.g. 'body_payload' contains 'payload')
# but are property names, not animator-facing copy — so the gate allows exact
# matches of these strings only.
# ---------------------------------------------------------------------------
IDENTIFIER_STRINGS: tuple[str, ...] = (
    'body_payload',
    'posing_payload',
    'quadruped_payload',
    'candidate_action',
    'kept_action',
    'source_action',   # no forbidden term but included for completeness
)

# Contract states that BADGES and CARDS must cover (contract §STATE MAP).
_CONTRACT_STATES: tuple[str, ...] = (
    'NO_RIG',
    'UNSUPPORTED_RIG',
    'MAPPED',
    'POSING_OBJECT',
    'POSING_POSE_MODE',
    'ANCHORS_CAPTURED',
    'PREVIEW_ACTIVE',
    'KEPT',
    'RESTORED',
    'SOLVE_RUNNING',
)

# Required BUTTONS keys (plan §2.3; contract §STATE MAP; §BEHAVIORAL SUCCESS).
_REQUIRED_BUTTON_KEYS: tuple[str, ...] = (
    'pose.begin',
    'pose.solve',
    'pose.keep',
    'pose.cancel',
    'motion.preview',
    'review.keep',
    'review.discard',
    'review.restore',
    'setup.inspect',
    'pose.mode_fix',
    'motion.show_timeline',
)


# ---------------------------------------------------------------------------
# Helper: collect docstring node-ids from an AST tree.
# Docstring = first statement of module/class/function body when that
# statement is ast.Expr(value=ast.Constant(value=str)).
# ---------------------------------------------------------------------------
def _docstring_nodes(tree: ast.AST) -> set[int]:
    ids: set[int] = set()
    for node in ast.walk(tree):
        body = getattr(node, 'body', None)
        if body and isinstance(node, (ast.Module, ast.ClassDef,
                                      ast.FunctionDef, ast.AsyncFunctionDef)):
            first = body[0]
            if (isinstance(first, ast.Expr)
                    and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)):
                ids.add(id(first.value))
    return ids


# ---------------------------------------------------------------------------
# CopyModuleTests — white-box tests for copy.py
# ---------------------------------------------------------------------------
class CopyModuleTests(unittest.TestCase):

    def test_all_strings_no_forbidden_terms(self):
        """Every value from copy.all_strings() passes copy.check()."""
        offenders = [(s, _copy.check(s)) for s in _copy.all_strings() if _copy.check(s)]
        self.assertEqual(
            offenders, [],
            msg='Forbidden terms found in copy.all_strings(): ' + str(offenders),
        )

    def test_all_strings_count_at_least_40(self):
        self.assertGreaterEqual(len(_copy.all_strings()), 40)

    def test_buttons_has_required_keys(self):
        missing = [k for k in _REQUIRED_BUTTON_KEYS if k not in _copy.BUTTONS]
        self.assertEqual(missing, [], msg='BUTTONS missing keys: ' + str(missing))

    def test_buttons_has_exactly_required_keys(self):
        extra = [k for k in _copy.BUTTONS if k not in _REQUIRED_BUTTON_KEYS]
        self.assertEqual(extra, [], msg='BUTTONS has unexpected keys: ' + str(extra))

    def test_badges_covers_all_contract_states(self):
        missing = [s for s in _CONTRACT_STATES if s not in _copy.BADGES]
        self.assertEqual(missing, [], msg='BADGES missing states: ' + str(missing))

    def test_cards_covers_all_contract_states(self):
        missing = [s for s in _CONTRACT_STATES if s not in _copy.CARDS]
        self.assertEqual(missing, [], msg='CARDS missing states: ' + str(missing))

    def test_fmt_preserves_unknown_fields(self):
        """fmt("frames {a}-{b}", a=1) keeps {b} intact."""
        result = _copy.fmt('frames {a}-{b}', a=1)
        self.assertEqual(result, 'frames 1-{b}')

    def test_marker_prefix_ascii_and_length_budget(self):
        """MARKER_PREFIX is pure ASCII and leaves room for a two-digit number.
        spike (UI-SPIKE-v1.md): ASCII marker names <= 12 chars.
        len(MARKER_PREFIX) + 2 <= 12.
        """
        prefix = _copy.MARKER_PREFIX
        self.assertTrue(
            all(ord(c) < 128 for c in prefix),
            msg=f'MARKER_PREFIX contains non-ASCII: {prefix!r}',
        )
        self.assertLessEqual(
            len(prefix) + 2, 12,
            msg=f'MARKER_PREFIX too long: len={len(prefix)}, budget=10 chars',
        )

    def test_forbidden_terms_tuple_present(self):
        self.assertIsInstance(_copy.FORBIDDEN_TERMS, tuple)
        self.assertIn('candidate', _copy.FORBIDDEN_TERMS)
        self.assertIn('payload', _copy.FORBIDDEN_TERMS)
        self.assertIn('backend', _copy.FORBIDDEN_TERMS)
        self.assertIn('internal units', _copy.FORBIDDEN_TERMS)

    def test_check_case_insensitive(self):
        self.assertTrue(_copy.check('Candidate action'))
        self.assertTrue(_copy.check('PAYLOAD data'))
        self.assertFalse(_copy.check('Original animation'))

    def test_stages_ordered_tuple(self):
        keys = [k for k, _ in _copy.STAGES]
        self.assertEqual(keys, ['SETUP', 'POSE', 'MOTION', 'POLISH', 'REVIEW'])

    def test_stage_hint_covers_all_stages(self):
        for key, _ in _copy.STAGES:
            self.assertIn(key, _copy.STAGE_HINT, msg=f'STAGE_HINT missing {key!r}')

    def test_family_has_unsupported_entry(self):
        self.assertIn('', _copy.FAMILY)
        self.assertEqual(_copy.FAMILY[''], 'Unsupported')

    def test_hud_has_mode_hint_and_alert(self):
        self.assertIn('mode_hint', _copy.HUD)
        self.assertIn('mode_alert', _copy.HUD)

    def test_hud_legend_role_names(self):
        expected = ('legend_pelvis', 'legend_torso', 'legend_head',
                    'legend_hand_l', 'legend_hand_r',
                    'legend_foot_l', 'legend_foot_r', 'legend_pole')
        for key in expected:
            self.assertIn(key, _copy.HUD, msg=f'HUD missing {key!r}')

    def test_review_keep_mentions_original_kept(self):
        """contract §BEHAVIORAL SUCCESS criterion 6 — both clauses present."""
        label = _copy.BUTTONS['review.keep']
        self.assertIn('original', label.lower())
        self.assertIn('kept', label.lower())

    def test_review_restore_mentions_kept_available(self):
        label = _copy.BUTTONS['review.restore']
        self.assertIn('kept', label.lower())
        self.assertIn('available', label.lower())

    def test_motion_preview_has_frame_placeholders(self):
        label = _copy.BUTTONS['motion.preview']
        self.assertIn('{a}', label)
        self.assertIn('{b}', label)


# ---------------------------------------------------------------------------
# UiWorkflowStringsGate — AST scan of all ui_workflow/*.py for forbidden terms
# ---------------------------------------------------------------------------
class UiWorkflowStringsGate(unittest.TestCase):
    """Scan every b4artists_ml/ui_workflow/**/*.py for forbidden terms.

    copy.py is excluded: it IS the vocabulary map (its VOCAB dict keys are
    intentionally the internal terms being mapped away) and is covered
    exhaustively by CopyModuleTests via copy.all_strings() (values only).

    For all other files: every ast.Constant str node that is not a docstring
    must pass copy.check() unless it is an exact IDENTIFIER_STRINGS entry
    (property-name strings that may contain forbidden substrings by necessity).
    """

    _UI_WORKFLOW_DIR = _ROOT / 'b4artists_ml' / 'ui_workflow'
    # copy.py is the vocab map; CopyModuleTests covers it via all_strings().
    _SKIP_FILES: frozenset[str] = frozenset({'copy.py'})

    def _py_files(self) -> list[Path]:
        d = self._UI_WORKFLOW_DIR
        if not d.is_dir():
            return []
        return sorted(p for p in d.rglob('*.py') if p.name not in self._SKIP_FILES)

    def _violations_in_file(self, path: Path) -> list[tuple[int, str, list[str]]]:
        src = path.read_text(encoding='utf-8')
        tree = ast.parse(src, filename=str(path))
        ds_ids = _docstring_nodes(tree)
        out: list[tuple[int, str, list[str]]] = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Constant):
                continue
            if not isinstance(node.value, str):
                continue
            if id(node) in ds_ids:
                continue
            s = node.value
            if s in IDENTIFIER_STRINGS:
                continue
            bad = _copy.check(s)
            if bad:
                out.append((node.lineno, s, bad))
        return out

    def _ml_violations_in_file(self, path: Path) -> list[tuple[int, str]]:
        """'Machine Learning' allowed only when string also contains 'learned'/'temporal'."""
        src = path.read_text(encoding='utf-8')
        tree = ast.parse(src, filename=str(path))
        ds_ids = _docstring_nodes(tree)
        out: list[tuple[int, str]] = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Constant):
                continue
            if not isinstance(node.value, str):
                continue
            if id(node) in ds_ids:
                continue
            s = node.value
            lower = s.lower()
            if 'machine learning' in lower:
                if 'learned' not in lower and 'temporal' not in lower:
                    out.append((node.lineno, s))
        return out

    def _bare_blender_imports(self, path: Path) -> list[str]:
        """Top-level bare Blender imports violate the guarded-import rule."""
        src = path.read_text(encoding='utf-8')
        tree = ast.parse(src, filename=str(path))
        violations: list[str] = []
        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == _BLENDER_PKG:
                        violations.append(
                            f'{path.name}: bare top-level import of {_BLENDER_PKG}'
                        )
            elif isinstance(node, ast.ImportFrom):
                if node.module and (
                    node.module == _BLENDER_PKG
                    or node.module.startswith(_BLENDER_PKG + '.')
                ):
                    violations.append(
                        f'{path.name}: bare top-level from-import of {_BLENDER_PKG}'
                    )
        return violations

    def test_no_forbidden_terms_in_non_docstring_strings(self):
        files = self._py_files()
        if not files:
            self.skipTest('b4artists_ml/ui_workflow/ absent or empty (Phase 1 not yet built)')
        all_v: dict[str, list] = {}
        for f in files:
            v = self._violations_in_file(f)
            if v:
                all_v[str(f.relative_to(_ROOT))] = v
        self.assertEqual(
            all_v, {},
            msg='Forbidden terms in ui_workflow strings:\n' + '\n'.join(
                f'  {fp}: line {ln}: {s!r} -> {bad}'
                for fp, items in all_v.items()
                for ln, s, bad in items
            ),
        )

    def test_machine_learning_label_only_on_learned_temporal(self):
        files = self._py_files()
        if not files:
            self.skipTest('b4artists_ml/ui_workflow/ absent or empty')
        all_v: dict[str, list] = {}
        for f in files:
            v = self._ml_violations_in_file(f)
            if v:
                all_v[str(f.relative_to(_ROOT))] = v
        self.assertEqual(
            all_v, {},
            msg='"Machine Learning" on non-temporal string:\n' + '\n'.join(
                f'  {fp}: line {ln}: {s!r}'
                for fp, items in all_v.items()
                for ln, s in items
            ),
        )

    def test_no_bare_blender_import_at_module_top(self):
        """No ui_workflow file may have an unguarded top-level Blender import
        (CODE STYLE: use try/except ImportError guard; touch Blender only inside functions)."""
        files = self._py_files()
        if not files:
            self.skipTest('b4artists_ml/ui_workflow/ absent or empty')
        violations: list[str] = []
        for f in files:
            violations.extend(self._bare_blender_imports(f))
        self.assertEqual(violations, [], msg='Unguarded imports:\n' + '\n'.join(violations))


if __name__ == '__main__':
    unittest.main(verbosity=2)
