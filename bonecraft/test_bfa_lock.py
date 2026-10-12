"""Simulate hosts with a fake bpy and exercise the BFA lock layers.

Run with:  python3 test_bfa_lock.py   (from the BoneForge-BFA-8.3.1 dir)
"""
import os, pathlib
BUILD_ROOT = str(pathlib.Path(__file__).resolve().parent)
import contextlib, io, sys, types, importlib

def make_fake_bpy(binary_path, bfa_attr, resource_base):
    bpy = types.ModuleType('bpy')

    class Timers:
        registered = []
        @classmethod
        def register(cls, fn, first_interval=0): cls.registered.append(fn)
        @classmethod
        def is_registered(cls, fn): return fn in cls.registered
        @classmethod
        def unregister(cls, fn):
            if fn in cls.registered:
                cls.registered.remove(fn)

    app = types.SimpleNamespace(binary_path=binary_path, timers=Timers,
                                version=(4, 5, 0))
    if bfa_attr:
        app.bforartists_version = bfa_attr
    bpy.app = app

    class Operator: pass
    class AddonPreferences: pass
    class FakeTypes:
        # Permissive: any other attribute becomes a dummy class so
        # module-level annotations/bases import fine. bpy.app stays
        # STRICT so detection results remain honest.
        def __getattr__(self, name):
            cls = type(name, (), {})
            setattr(self, name, cls)
            return cls
    registered = []
    types_mod = types.ModuleType('bpy.types')
    types_mod.Operator = Operator
    types_mod.AddonPreferences = AddonPreferences
    def _types_getattr(name):
        cls = type(name, (), {})
        setattr(types_mod, name, cls)
        return cls
    types_mod.__getattr__ = _types_getattr
    bpy.types = types_mod

    props_mod = types.ModuleType('bpy.props')
    props_mod.__getattr__ = lambda name: (lambda *a, **kw: None)
    bpy.props = props_mod

    utils_mod = types.ModuleType('bpy.utils')
    utils_mod.register_class = lambda c: registered.append(c)
    def _unregister_class(c):
        if c in registered:
            registered.remove(c)
    utils_mod.unregister_class = _unregister_class
    app.handlers = types.SimpleNamespace(persistent=lambda f: f,
                                         load_post=[], save_pre=[])
    bpy._submodules = {'bpy.types': types_mod, 'bpy.props': props_mod,
                       'bpy.utils': utils_mod}

    utils_mod.resource_path = lambda kind: {
        'USER': resource_base + '/user', 'LOCAL': resource_base + '/local',
        'SYSTEM': resource_base + '/system'}[kind]
    bpy.utils = utils_mod
    bpy._registered = registered
    bpy.context = types.SimpleNamespace(window_manager=None)
    bpy.ops = types.SimpleNamespace(
        wm=types.SimpleNamespace(url_open=lambda url: None))
    return bpy

def fresh_import(bpy):
    for name in [n for n in list(sys.modules) if n == 'boneforge' or n.startswith('boneforge.')]:
        del sys.modules[name]
    for mod_name in ('bpy.types', 'bpy.props', 'bpy.utils'):
        sys.modules.pop(mod_name, None)
    sys.modules['bpy'] = bpy
    sys.modules.update(bpy._submodules)
    if BUILD_ROOT not in sys.path:
        sys.path.insert(0, BUILD_ROOT)
    import boneforge
    return boneforge

# ---------- Scenario 1: standard Blender ----------
bpy = make_fake_bpy(
    r'C:\Program Files\Blender Foundation\Blender 4.5\blender.exe',
    None, r'C:\Users\ax\AppData\Roaming\Blender Foundation\Blender\4.5')
bf = fresh_import(bpy)
from boneforge import bfa_guard
assert bfa_guard.detection_signals() == [], bfa_guard.detection_signals()
assert not bfa_guard.is_bforartists()
assert not bf._bfa_environment_ok()

with contextlib.redirect_stderr(io.StringIO()):
    bf.register()
assert bf._lockout_active, 'lockout flag not set'
names = sorted(c.__name__ for c in bpy._registered)
assert names == ['BONEFORGE_OT_get_bforartists', 'BoneForgeLockedPreferences'], names
# Nothing functional was imported:
loaded = [n for n in sys.modules if n.startswith('boneforge.')]
assert set(loaded) == {'boneforge.bfa_guard'}, loaded
print('S1a standard Blender: lockout-only register PASS  (registered: %s)' % names)

# Layer 2: core raises independently
from boneforge import core as bf_core
try:
    bf_core.register(); raise SystemExit('FAIL: core registered in Blender!')
except RuntimeError as e:
    print('S1b core gate raises PASS  (%s...)' % str(e)[:48])

# Layer 3: registry refuses independently
from boneforge.core import tool_registry as tr
try:
    tr.get_registry(); raise SystemExit('FAIL: registry handed out in Blender!')
except RuntimeError as e:
    print('S1c registry gate raises PASS  (%s...)' % str(e)[:48])

# Lockout unregister round-trip
bf.unregister()
assert bpy._registered == [], bpy._registered
assert not bf._lockout_active
print('S1d lockout unregister round-trip PASS')

# Strengthened exclusivity (rev 2): the new gap-closure modules must
# never import or register under standard Blender.
_GAP_MODULES = (
    'boneforge.autorig.rig_build', 'boneforge.autorig.components',
    'boneforge.core.rig_ops', 'boneforge.weights.widgets',
    'boneforge.autorig.maps', 'boneforge.autorig.geo_detect',
    'boneforge.io_hub.profiles', 'boneforge.control_ui',
    'boneforge.advanced_rigging.control_layer',
    'boneforge.advanced_rigging.control_math',
    'boneforge.io_hub.profile_export',
    'boneforge.autorig.components.face',
    'boneforge.autorig.retarget_core',
    'boneforge.autorig.rig_integrate',
    'boneforge.autorig.joint_correctives',
    'boneforge.autorig.face_controls',
    'boneforge.autorig.skirt_rig',
)
for _m in _GAP_MODULES:
    assert _m not in sys.modules, 'gap module loaded in standard Blender: ' + _m
print('S1e new gap modules absent in standard Blender PASS')

# ---------- Scenario 2: Bforartists (attr + paths) ----------
bpy2 = make_fake_bpy(
    r'C:\Program Files\Bforartists 5\bforartists.exe',
    (5, 0, 0), r'C:\Users\ax\AppData\Roaming\Bforartists\Bforartists\5.0')
bf2 = fresh_import(bpy2)
from boneforge import bfa_guard as g2
sig = g2.detection_signals()
assert 'app.bforartists_version' in sig and 'binary_path' in sig, sig
assert g2.is_bforartists() and bf2._bfa_environment_ok()
from boneforge import core as core2
core2._require_bfa_host()  # must NOT raise
from boneforge.core import tool_registry as tr2
assert tr2._verify_bfa_host() is True
print('S2 Bforartists: all gates open PASS  (signals: %s)' % sig)

# ---------- Scenario 3: BFA without the version attr (older builds) ----------
bpy3 = make_fake_bpy('/opt/bforartists/bforartists', None,
                     '/home/ax/.config/bforartists/5.0')
bf3 = fresh_import(bpy3)
from boneforge import bfa_guard as g3
assert g3.is_bforartists() and bf3._bfa_environment_ok(), g3.detection_signals()
print('S3 BFA w/o version attr: gates open PASS  (signals: %s)' % g3.detection_signals())

# ---------- Scenario 4: re-verify timer flips to lockout ----------
bpy4 = make_fake_bpy(
    r'C:\Program Files\Bforartists 5\bforartists.exe',
    (5, 0, 0), r'C:\Users\ax\AppData\Roaming\Bforartists\Bforartists\5.0')
bf4 = fresh_import(bpy4)
bf4._reverify_enabled = True
assert bf4._bfa_reverify() == 600.0   # healthy -> reschedule
# simulate host signals vanishing (tamper) mid-session:
del bpy4.app.bforartists_version
bpy4.app.binary_path = r'C:\x\blender.exe'
bpy4.utils.resource_path = lambda kind: r'C:\x\blender\4.5'
with contextlib.redirect_stderr(io.StringIO()):
    assert bf4._bfa_reverify() is None    # tripped -> stop timer
assert bf4._lockout_active
assert sorted(c.__name__ for c in bpy4._registered) == [
    'BONEFORGE_OT_get_bforartists', 'BoneForgeLockedPreferences']
print('S4 timer re-verify trips to lockout PASS')

print('\nALL LOCK TESTS PASS')
