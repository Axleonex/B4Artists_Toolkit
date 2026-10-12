"""Targeted Bforartists regression suite for the starter catalog."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.dirname(HERE), HERE]

for name in ('test_starter_shelf_host', 'test_quick_rigs_asset_host',
             'test_rig_assets_host', 'test_dropped_rig_host', 'test_ui_access_host'):
    __import__(name).run()
    print('RESULT OK', name)
