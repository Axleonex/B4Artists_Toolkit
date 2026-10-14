# Anim Assist 12.6.0

Anim Assist is an animation add-on for Bforartists, the Blender fork. Install it
in your existing Bforartists application. Standard Blender remains unsupported.

## Timeline tools

The existing Timeline header provides seven tool families: Tween, Curves,
Timing, Keys, Pose, Bake and Motion. Configurable quick buttons, Search, Pin
and nearby options expose 89 existing actions. Pin an action for direct access;
use the Gear to configure quick selections or Reset.

This add-on does not create a second native Timeline row. It no longer creates
a separate Text Editor strip or repeatedly repairs editor geometry.
The custom Windows application has been withdrawn from distribution.

## Download and install

Download [b4_anim_assist_v12.6.0.zip](https://github.com/Axleonex/B4Artists_Toolkit/releases/download/v12.6.0/b4_anim_assist_v12.6.0.zip).

1. Open **Edit > Preferences > Add-ons > Install from Disk** in Bforartists.
2. Select the ZIP without extracting it.
3. Enable Anim Assist and restart Bforartists after updating.
4. Open a Timeline and use its Anim Assist controls.

The ZIP is 577,101 bytes. SHA256:
`60d4c7f10d9f14adde17e0cd5269bb07d4a4fc8f96810a4cd6e67903e5e73193`.

## Fixes and validation

- Explained and enforced Ease's two-key prerequisite.
- Fixed Action Offset package preferences, handle translation and cancellation
  of keys, selection and custom easing settings.
- All 80 immediate tool effects passed in standard Bforartists.
- Nine modal commit/cancel pairs and additional layout checks passed in the
  withdrawn custom application. Those results are historical and do not claim
  equivalent modal or layout coverage in standard Bforartists.

The add-on ZIP is unchanged by this distribution cleanup. Historical
[qualification](qualification.md) and [tool access coverage](tool-access-coverage.md)
retain the original host-specific evidence. Full AnimBot algorithm parity and
exhaustive production-rig coverage are not established.
