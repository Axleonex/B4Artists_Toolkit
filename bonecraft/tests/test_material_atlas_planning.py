import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLANNING = (
    ROOT
    / "boneforge"
    / "vrchat"
    / "cats"
    / "material_atlas_planning.py"
)


def _load_planning_module():
    spec = importlib.util.spec_from_file_location(
        "boneforge_material_atlas_planning",
        PLANNING,
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_mixed_mesh_keeps_alpha_blend_out_of_opaque_atlas():
    planning = _load_planning_module()

    groups = planning.plan_material_slot_groups(
        [
            {
                "object_name": "Body",
                "slot_index": 0,
                "render_type": "Opaque",
            },
            {
                "object_name": "Body",
                "slot_index": 1,
                "render_type": "Opaque",
            },
            {
                "object_name": "Body",
                "slot_index": 2,
                "render_type": "Alpha Blend",
            },
        ]
    )

    assert groups == [
        {
            "render_type": "Opaque",
            "enabled": True,
            "preserve_reason": "",
            "slots": [
                {
                    "object_name": "Body",
                    "slot_index": 0,
                    "render_type": "Opaque",
                },
                {
                    "object_name": "Body",
                    "slot_index": 1,
                    "render_type": "Opaque",
                },
            ],
        },
        {
            "render_type": "Alpha Blend",
            "enabled": False,
            "preserve_reason": "render_order",
            "slots": [
                {
                    "object_name": "Body",
                    "slot_index": 2,
                    "render_type": "Alpha Blend",
                }
            ],
        },
    ]


def test_unused_material_slots_do_not_enter_atlas_plan():
    planning = _load_planning_module()

    groups = planning.plan_material_slot_groups(
        [
            {
                "object_name": "Body",
                "slot_index": 0,
                "render_type": "Opaque",
                "has_faces": True,
            },
            {
                "object_name": "Body",
                "slot_index": 1,
                "render_type": "Opaque",
                "has_faces": True,
            },
            {
                "object_name": "Body",
                "slot_index": 4,
                "render_type": "Opaque",
                "has_faces": False,
            },
        ]
    )

    assert [slot["slot_index"] for slot in groups[0]["slots"]] == [0, 1]
    assert groups[0]["enabled"] is True


def test_multiple_alpha_blend_materials_remain_preserved_by_default():
    planning = _load_planning_module()

    groups = planning.plan_material_slot_groups(
        [
            {
                "object_name": "Hair",
                "slot_index": 0,
                "render_type": "Alpha Blend",
            },
            {
                "object_name": "Clothes",
                "slot_index": 3,
                "render_type": "Alpha Blend",
            },
        ]
    )

    assert groups == [
        {
            "render_type": "Alpha Blend",
            "enabled": False,
            "preserve_reason": "render_order",
            "slots": [
                {
                    "object_name": "Hair",
                    "slot_index": 0,
                    "render_type": "Alpha Blend",
                },
                {
                    "object_name": "Clothes",
                    "slot_index": 3,
                    "render_type": "Alpha Blend",
                },
            ],
        }
    ]
