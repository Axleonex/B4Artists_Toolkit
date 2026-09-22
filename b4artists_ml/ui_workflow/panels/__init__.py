"""panels package — B4Artists ML UI workflow panel registry.

Plan §2.1: declares registration order for all side-panel modules.
No bpy or sibling imports; package is inert for pure-Python import trees.
"""

PANEL_MODULES = ('setup', 'pose', 'motion', 'review', 'polish', 'advanced')
