"""Animator-facing strings for B4Artists ML.

All labels, badges, hints, and button copy for the five panels live here so the
forbidden-term rule (plan §2.4; contract §FAILURE, §BEHAVIORAL SUCCESS, §DESIGN PLAN)
is greppable and testable in one place.

Verified source sections:
  UI-ARCHITECTURE-PLAN-v1.md §2.4 vocabulary table, §3 panel descriptions
  UI-EXPERIENCE-CONTRACT-v1.md §STATE MAP presentation column,
    §FAILURE user-side descriptions, §BEHAVIORAL SUCCESS button-copy requirements,
    §DESIGN PLAN
"""

# ---------------------------------------------------------------------------
# Vocabulary guard
# ---------------------------------------------------------------------------

# "Machine Learning" may label only the learned temporal path; everything else
# says "procedural".
FORBIDDEN_TERMS: tuple[str, ...] = (
    'candidate',
    'payload',
    'backend',
    'internal units',
)

LEARNED_LABEL_ONLY_FOR: tuple[str, ...] = ('temporal',)

# ---------------------------------------------------------------------------
# Vocabulary (plan §2.4)
# ---------------------------------------------------------------------------

VOCAB: dict[str, str] = {
    'source action':        'Original animation',
    'candidate action':     'Preview',
    'kept action':          'Kept result',
    'anchor':               'Key pose',
    'body_payload session': 'Posing session',
    'backend':              'Method',
}

# ---------------------------------------------------------------------------
# Stages
# ---------------------------------------------------------------------------

STAGES: tuple[tuple[str, str], ...] = (
    ('SETUP',   'Setup'),
    ('POSE',    'Pose'),
    ('MOTION',  'Motion'),
    ('POLISH',  'Polish'),
    ('REVIEW',  'Review'),
)

STAGE_HINT: dict[str, str] = {
    'SETUP':   'Select a rig and confirm the mapping.',
    'POSE':    'Capture key poses on the character.',
    'MOTION':  'Generate interpolated motion between key poses.',
    'POLISH':  'Refine contacts, cleanup, and secondary motion.',
    'REVIEW':  'Keep or discard the generated motion.',
}

# Stage progress line template; header.prelude formats it with fmt()
# using keys n (1-based index), total (len(STAGES)), label (stage display name).
STAGE_LINE: str = 'Stage {n} of {total} — {label}'

# ---------------------------------------------------------------------------
# Button labels (plan §2.3 action keys; contract §STATE MAP; §BEHAVIORAL SUCCESS)
# ---------------------------------------------------------------------------

BUTTONS: dict[str, str] = {
    'pose.begin':         'Start Posing',
    'pose.solve':         'Solve',
    'pose.keep':          'Keep Pose',
    'pose.cancel':        'Cancel Posing',
    # {a} and {b} are frame-range placeholders; use fmt() to fill them.
    'motion.preview':     'Generate Preview (frames {a}-{b})',
    # contract §BEHAVIORAL SUCCESS criterion 6: copy must explain what is kept
    'review.keep':        'Keep (saves the preview as a new action; the original is kept too)',
    'review.discard':     'Discard (returns to the original animation)',
    'review.restore':     'Restore Original (the kept result stays available)',
    'setup.inspect':      'Check Rig',
    'pose.mode_fix':      'Switch to Object Mode',
    'motion.show_timeline': 'Show Timeline',
}

# ---------------------------------------------------------------------------
# State badges (contract §STATE MAP presentation column)
# ---------------------------------------------------------------------------

# {name} is the action name placeholder; use fmt() to fill it.
BADGES: dict[str, str] = {
    'NO_RIG':          '',
    'UNSUPPORTED_RIG': 'Not supported',
    'MAPPED':          'Original animation',
    'POSING_OBJECT':   'Posing session active',
    'POSING_POSE_MODE': 'Posing session active',
    'ANCHORS_CAPTURED': 'Key poses ready',
    'PREVIEW_ACTIVE':  'Previewing: {name}',
    'KEPT':            'Kept: {name}',
    'RESTORED':        'Original restored',
    'SOLVE_RUNNING':   'Generating\u2026',
}

FAMILY: dict[str, str] = {
    'HUMANOID':   'Humanoid',
    'QUADRUPED':  'Quadruped',
    '':           'Unsupported',
}

# ---------------------------------------------------------------------------
# Cards — presentation line per state (contract §STATE MAP, Presentation column)
# ---------------------------------------------------------------------------

CARDS: dict[str, str] = {
    'NO_RIG':           'Select an armature or a mesh bound to one.',
    'UNSUPPORTED_RIG':  'This rig is not supported \u2014 Check Rig for details.',
    'MAPPED':           'Rig mapped. Capture key poses to continue.',
    'POSING_OBJECT':    'Move targets in Object Mode, then Solve.',
    'POSING_POSE_MODE': 'Move targets in Object Mode \u2014 switch now.',
    'ANCHORS_CAPTURED': 'Key poses ready. Generate a motion preview.',
    'PREVIEW_ACTIVE':   'Previewing generated motion. Keep or discard.',
    'KEPT':             'Motion kept. Original animation is still available.',
    'RESTORED':         'Original action and input rig modes restored; kept result remains in Actions.',
    'SOLVE_RUNNING':    'Generating \u2014 wait for the current task to finish.',
}

NEXT_PREFIX: str = 'Next:'

# ---------------------------------------------------------------------------
# Per-subpanel prerequisite / description lines (Advanced panel subpanels).
# Keys: bl_label lowercased with spaces as underscores.
# Values: the exact label(s) drawn by each subpanel after the rig-None check.
# Where a subpanel draws a Procedural tag, both strings are stored as a tuple
# so all_strings() / check() can validate them together.
# ---------------------------------------------------------------------------

PREREQ: dict[str, object] = {
    'rig_mapping':      'Maps bone controls to semantic roles.',
    'assisted_pose':    'Geometric IK-to-FK solver and whole-body pose for humanoid rigs.',
    'quadruped':        'Four-paw whole-body pose for Rigify quadruped rigs.',
    'center_of_mass':   'Artist-authored mass estimate for stability analysis.',
    'contacts':         'Needs a preview or kept result.',
    'airborne':         'Needs a preview or kept result.',
    'cleanup':          ('Needs a preview or kept result.',
                         'Procedural cleanup; no learned model used.'),
    'secondary_motion': 'Needs a preview or kept result.',
    'saved_results':    'Previously kept motion results for this rig.',
}

# ---------------------------------------------------------------------------
# HUD viewport strings (Phase 2, plan §4; contract §DESIGN PLAN)
# ---------------------------------------------------------------------------

HUD: dict[str, str] = {
    'mode_hint':        'Move targets in Object Mode',
    'mode_alert':       'Switch to Object Mode',
    'legend_pelvis':    'Pelvis',
    'legend_torso':     'Torso',
    'legend_head':      'Head',
    'legend_hand_l':    'Hand L',
    'legend_hand_r':    'Hand R',
    'legend_foot_l':    'Foot L',
    'legend_foot_r':    'Foot R',
    'legend_pole':      'Pole',
}

# Marker name prefix: ASCII, per spike (UI-SPIKE-v1.md).
MARKER_PREFIX: str = 'B4ML Pose '

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def check(text: str) -> list[str]:
    """Return list of forbidden terms found in *text* (case-insensitive)."""
    lower = text.lower()
    return [t for t in FORBIDDEN_TERMS if t.lower() in lower]


class _DefaultDict(dict):
    """dict subclass whose __missing__ returns the braced key intact."""
    def __missing__(self, key: str) -> str:
        return '{' + key + '}'


def fmt(template: str, **kw) -> str:
    """Format *template* with str.format_map; unknown fields stay as {field}."""
    return template.format_map(_DefaultDict(kw))


def _collect(obj) -> list[str]:
    """Recursively collect all string values from dicts/tuples/lists."""
    if isinstance(obj, str):
        return [obj]
    if isinstance(obj, dict):
        result: list[str] = []
        for v in obj.values():
            result.extend(_collect(v))
        return result
    if isinstance(obj, (list, tuple)):
        result = []
        for item in obj:
            result.extend(_collect(item))
        return result
    return []


def all_strings() -> list[str]:
    """Every string value in the module's public tables (keys excluded).

    The copy test iterates this to check for forbidden terms.
    """
    tables = [
        VOCAB,
        STAGES,
        STAGE_HINT,
        STAGE_LINE,
        BUTTONS,
        BADGES,
        FAMILY,
        CARDS,
        NEXT_PREFIX,
        HUD,
        MARKER_PREFIX,
        PREREQ,
    ]
    result: list[str] = []
    for table in tables:
        result.extend(_collect(table))
    return result
