# UI and interaction contract

SUBJECT: Anim Assist second Timeline row for rapid animation adjustment.
TREATMENT: ui-tool; compact existing desktop editor conventions.
PALETTE: ground #303030, surface #383838, control #484848, ink #F0F0F0,
secondary #B8B8B8, primary accent #55C7D0. Derive actual neutrals/text/focus
from the host theme. Family icon accents may differ; labels and shapes also
communicate meaning. Never depend on color alone.
TYPE: host BLF sans-serif, baseline 11 logical px, UI-scale aware.
LAYOUT: one header-height canvas band; labels/icons/slider tracks horizontally
grouped in approved family order, utilities anchored right. No tutorial cards.

## States and visible success

| State | Visible behavior | Data behavior |
| --- | --- | --- |
| Idle valid | Two default tracks, numeric readouts, labels | Drawing does not write animation/settings |
| Disabled | Family/control stays visible with prerequisite tooltip | No gesture or mutation |
| Inline drag | Track/handle/value follows pointer | Absolute preview from start snapshot |
| Popout drag | Track anchored within canvas near fixed icon | Same transaction semantics as inline |
| Commit | Popout disappears; value feedback reflects result | One undo record; target effect asserted |
| Cancel/error | Popout disappears, original readout restored | Keys, handles, pose, selection and touched scene settings restored |
| Settings | Native staged dialog; supported fields only | Cancel leaves configuration unchanged |
| Layout edit | Named layout marked modified | Animation unchanged; library unchanged until explicit save/update |
| Load/reset | Row updates; chosen layout name shown in Settings | Presentation only; stored other layouts preserved |

Right-click while idle opens tool settings, with explicit equivalent in Toolbar
Settings. During a gesture it cancels. Track clicks begin the hold/release
transaction; no separate mode selection or Apply button. Precision, numeric
entry, reset and presets route through the same undoable operation. Show
Breakdown anchor explanation and actual clipboard/time/pose scope in tooltips.

## Responsive and accessibility gates

Widths 250/480/800/1164/1920 logical px; UI scales 1/1.5/2. Pure geometry tests
cover all cells; real-window cells beyond monitor size are unverified. Compact
labels/buttons first, then temporarily use popout form for tracks, then More.
No rectangles overlap or exceed bounds. User configuration remains identical
after shrinking/expanding. Track widths configurable 80–240 logical px, default
120. Compact desktop target minimum 24 logical px where host row permits;
measure contrast with active theme, body text >=4.5:1 and controls >=3:1.
When a native-sized canvas cannot meet these dimensions, report the limitation
instead of silently repairing editor geometry.

Keyboard access through Search and native dialogs, focus indicators, text names
on icons, and immediate prerequisites help users discover direct drag. No
continuous pointer interception while idle. Settings/load/resize are forbidden
during active drag until commit/cancel (or cancel the drag explicitly first).

## Human usability check

Owner can identify and drag Breakdown without a submenu, discover tool settings,
pin/unpin Smooth, name two layouts and switch them, cancel a timing adjustment,
then scrub/play the native Timeline. Record actual outcomes separately from
automated gates. Do not call the UI intuitive solely because it matches an
image. Mockup titles and explanatory annotations never enter product UI.
