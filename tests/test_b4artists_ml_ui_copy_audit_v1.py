"""Whole-addon copy audit for b4artists_ml/ui.py.

Handoff §Human usability acceptance: terms candidate_action, payload, backend,
and internal units must not appear in animator-facing copy.

Extends the ui_workflow gate (test_b4artists_ml_ui_copy_v1.py) to cover
b4artists_ml/ui.py itself — its text= labels, self.report messages,
bl_label values, and state.status assignment literals are all animator-facing.

PROP_CALLS / ATTR_CALLS / IDENTIFIER_STRINGS are copied verbatim from
tests/test_b4artists_ml_ui_copy_v1.py.  Duplication is intentional: test
files must not import each other via package machinery that requires the
Blender runtime; loading one test file from another with importlib would pull
in _load_copy() and the copy module at import time, coupling both files.
"""

import ast
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent

# ---------------------------------------------------------------------------
# Copied verbatim from tests/test_b4artists_ml_ui_copy_v1.py (see docstring).
# ---------------------------------------------------------------------------
PROP_CALLS: tuple[str, ...] = (
    'prop', 'prop_enum', 'prop_search', 'prop_menu_enum',
    'template_list', 'prop_with_popover', 'prop_decorator',
)
_PROP_KW_NAMES: frozenset[str] = frozenset({
    'property', 'propname', 'dataptr',
    'active_propname', 'listtype_name', 'list_id',
})
ATTR_CALLS: tuple[str, ...] = ('getattr', 'setattr', 'hasattr', 'delattr')

IDENTIFIER_STRINGS: tuple[str, ...] = (
    'body_payload',
    'posing_payload',
    'quadruped_payload',
    'candidate_action',
    'kept_action',
    'source_action',
)
# ---------------------------------------------------------------------------

_FORBIDDEN_TERMS: tuple[str, ...] = ('candidate', 'payload', 'backend', 'internal units')


def _docstring_nodes(tree: ast.AST) -> set[int]:
    """Return id() of every Constant node that is a module/class/function docstring."""
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


def _prop_ident_exempt(tree: ast.AST) -> set[int]:
    """Return id() of Constant nodes that are property-identifier arguments.

    Mirrors UiWorkflowStringsGate._prop_ident_exempt from
    tests/test_b4artists_ml_ui_copy_v1.py — layout.prop second positional arg,
    RNA keyword names, getattr/setattr attribute names, and dict-subscript keys.
    The text= keyword is NOT exempted and stays checked.
    """
    exempt: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr in PROP_CALLS:
                for i, arg in enumerate(node.args):
                    if i == 0:
                        continue
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        exempt.add(id(arg))
                for kw in node.keywords:
                    if kw.arg in _PROP_KW_NAMES:
                        if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                            exempt.add(id(kw.value))
            if isinstance(func, ast.Name) and func.id in ATTR_CALLS:
                for i, arg in enumerate(node.args):
                    if i == 0:
                        continue
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        exempt.add(id(arg))
        elif isinstance(node, ast.Subscript):
            slc = node.slice
            if isinstance(slc, ast.Constant) and isinstance(slc.value, str):
                exempt.add(id(slc))
    return exempt


class UiPyCopyAuditTests(unittest.TestCase):
    """AST scan of b4artists_ml/ui.py for forbidden terms in animator-facing strings.

    Animator-facing string categories:
      (a) text= keyword value of .label() or .operator() calls
      (b) message argument (index 1) of .report() calls
      (c) bl_label class attribute string values
      (d) RHS string literal of <name>.status = ... assignments

    Same PROP_CALLS / ATTR_CALLS / IDENTIFIER_STRINGS exemptions as the
    ui_workflow gate in test_b4artists_ml_ui_copy_v1.py.

    If real violations exist in ui.py this test will FAIL and list every
    offending line and text verbatim — do NOT edit ui.py inside this packet;
    file a separate exact-replace packet from that list.
    """

    _UI_PY = _ROOT / 'b4artists_ml' / 'ui.py'

    def _parse_ui(self) -> ast.Module:
        src = self._UI_PY.read_text(encoding='utf-8')
        return ast.parse(src, filename=str(self._UI_PY))

    def _collect_animator_strings(self, tree: ast.AST) -> list[tuple[int, str]]:
        """Return (lineno, value) for every animator-facing string constant in ui.py."""
        ds_ids = _docstring_nodes(tree)
        prop_ids = _prop_ident_exempt(tree)
        found: list[tuple[int, str]] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                # (a) text= keyword in .label() or .operator()
                if isinstance(func, ast.Attribute) and func.attr in ('label', 'operator'):
                    for kw in node.keywords:
                        if kw.arg == 'text':
                            v = kw.value
                            if (isinstance(v, ast.Constant) and isinstance(v.value, str)
                                    and id(v) not in ds_ids and id(v) not in prop_ids):
                                found.append((v.lineno, v.value))
                # (b) .report() — arg index 1 is the animator-visible message
                if isinstance(func, ast.Attribute) and func.attr == 'report':
                    if len(node.args) >= 2:
                        msg = node.args[1]
                        if (isinstance(msg, ast.Constant) and isinstance(msg.value, str)
                                and id(msg) not in ds_ids):
                            found.append((msg.lineno, msg.value))

        # (c) bl_label class attribute values
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for stmt in node.body:
                    if isinstance(stmt, ast.Assign):
                        for tgt in stmt.targets:
                            if isinstance(tgt, ast.Name) and tgt.id == 'bl_label':
                                v = stmt.value
                                if isinstance(v, ast.Constant) and isinstance(v.value, str):
                                    found.append((v.lineno, v.value))

        # (d) <name>.status = <string literal>
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for tgt in node.targets:
                    if isinstance(tgt, ast.Attribute) and tgt.attr == 'status':
                        v = node.value
                        if (isinstance(v, ast.Constant) and isinstance(v.value, str)
                                and id(v) not in ds_ids):
                            found.append((v.lineno, v.value))

        return found

    # ------------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------------

    def test_parse_ui_py(self):
        """ui.py must parse without SyntaxError — prerequisite for all checks."""
        tree = self._parse_ui()
        self.assertIsInstance(tree, ast.Module)

    def test_animator_strings_collected_nonzero(self):
        """Collector finds at least one string — gate is not vacuous."""
        tree = self._parse_ui()
        strings = self._collect_animator_strings(tree)
        self.assertGreater(
            len(strings), 0,
            msg='No animator-facing strings collected from ui.py — gate is vacuous',
        )

    def test_no_forbidden_terms_in_animator_strings(self):
        """No animator-facing string in ui.py contains a forbidden term.

        If this fails the assertion lists every offending line and text so a
        separate exact-replace packet can fix each one without re-running discovery.
        """
        tree = self._parse_ui()
        strings = self._collect_animator_strings(tree)
        violations: list[str] = []
        for lineno, s in strings:
            if s in IDENTIFIER_STRINGS:
                continue
            bad = [t for t in _FORBIDDEN_TERMS if t in s.lower()]
            if bad:
                violations.append(f'  line {lineno}: {s!r} -> {bad}')
        self.assertEqual(
            violations, [],
            msg='Forbidden terms in ui.py animator-facing strings:\n' + '\n'.join(violations),
        )

    def test_machine_learning_label_only_on_learned_temporal(self):
        """'Machine Learning' in animator strings only when string contains 'learned'/'temporal'."""
        tree = self._parse_ui()
        strings = self._collect_animator_strings(tree)
        violations: list[str] = []
        for lineno, s in strings:
            lower = s.lower()
            if 'machine learning' in lower:
                if 'learned' not in lower and 'temporal' not in lower:
                    violations.append(f'  line {lineno}: {s!r}')
        self.assertEqual(
            violations, [],
            msg='"Machine Learning" on non-temporal string in ui.py:\n' + '\n'.join(violations),
        )


if __name__ == '__main__':
    unittest.main(verbosity=2)
