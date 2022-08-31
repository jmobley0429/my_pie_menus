import bpy

KEYMAP_SETTINGS = [
    {
        "keymap_operator": "wm.call_menu_pie",
        "name": "3D View",
        "letter": "A",
        "shift": 1,
        "ctrl": 0,
        "alt": 0,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {"name": "PIE_MT_AddMesh"}

    },
    {
        "keymap_operator": "wm.call_menu_pie",
        "name": "Object Mode",
        "letter": "O",
        "shift": 1,
        "ctrl": 0,
        "alt": 1,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {"name": "PIE_MT_sort_objects"}

    },
    {
        "keymap_operator": "wm.call_menu_pie",
        "name": "Mesh",
        "letter": "A",
        "shift": 1,
        "ctrl": 0,
        "alt": 0,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {"name": "PIE_MT_AddMesh"}

    },
    {
        "keymap_operator": "wm.call_menu_pie",
        "name": "3D View",
        "letter": "A",
        "shift": 1,
        "ctrl": 1,
        "alt": 0,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {"name": "PIE_MT_AddOtherObjects"}

    },
    {
        "keymap_operator": "mesh.reduce_cylinder",
        "name": "Mesh",
        "letter": "X",
       "shift": 1,
        "ctrl": 0,
        "alt": 1,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {}
    },
    {
        "keymap_operator": "wm.call_menu_pie",
        "name": "3D View Generic",
        "letter": "Q",
        "shift": 1,
        "ctrl": 1,
        "alt": 0,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {"name": "PIE_MT_AddModifier"}

    },
    {
        "keymap_operator": "wm.call_menu_pie",
        "name": "Object Mode",
        "letter": "C",
        "shift": 0,
        "ctrl": 0,
        "alt": 1,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {"name": "PIE_MT_ConvertMeshCurve"}
    },
    {
        "keymap_operator": "node.align",
        "name": "Node Editor",
        "letter": "W",
        "shift": 1,
        "ctrl": 0,
        "alt": 1,
        "space_type": "NODE_EDITOR",
        "region_type": "WINDOW",
        "keywords":{"direction":"TOP"}
    },
    {
        "keymap_operator": "node.align",
        "name": "Node Editor",
        "letter": "S",
        "shift": 1,
        "ctrl": 0,
        "alt": 1,
        "space_type": "NODE_EDITOR",
        "region_type": "WINDOW",
        "keywords":{"direction":"BOTTOM"}
    },
    {
        "keymap_operator": "node.align",
        "name": "Node Editor",
        "letter": "D",
        "shift": 1,
        "ctrl": 0,
        "alt": 1,
        "space_type": "NODE_EDITOR",
        "region_type": "WINDOW",
        "keywords":{"direction":"RIGHT"}
    },
    {
        "keymap_operator": "node.align",
        "name": "Node Editor",
        "letter": "A",
        "shift": 1,
        "ctrl": 0,
        "alt": 1,
        "space_type": "NODE_EDITOR",
        "region_type": "WINDOW",
        "keywords":{"direction":"LEFT"}
    },
    {
        "keymap_operator": "wm.call_menu_pie",
        "name": "Mesh",
        "letter": "ONE",
        "shift": False,
        "ctrl": False,
        "alt": True,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {"name": "MESH_MT_PIE_loop_tools"}
    },
    {
        "keymap_operator": "wm.call_menu_pie",
        "name": "Mesh",
        "letter": "Q",
        "shift": True,
        "ctrl": False,
        "alt": False,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {"name": "MESH_MT_PIE_symmetrize"}
    },
    {
        "keymap_operator": "wm.call_menu_pie",
        "name": "Mesh",
        "letter": "E",
        "shift": True,
        "ctrl": True,
        "alt": False,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {"name": "MESH_MT_edge_menu"}
    },
    {
        "keymap_operator": "wm.call_menu_pie",
        "name": "Mesh",
        "letter": "E",
        "shift": True,
        "ctrl": True,
        "alt": False,
        "space_type": "VIEW_3D",
        "region_type": "WINDOW",
        "keywords": {"name": "MESH_MT_face_menu"}
    },
]



def get_existing_keymap_items(name):
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.default.keymaps
    return kc[name].keymap_items[:]


def register_keymaps():
    print(KEYMAP_SETTINGS)
    for keymap in KEYMAP_SETTINGS:

        keymap_operator = keymap.pop("keymap_operator")
        name = keymap.pop("name")
        letter = keymap.pop("letter")
        shift = keymap.pop("shift")
        ctrl = keymap.pop("ctrl")
        alt = keymap.pop("alt")
        space_type = keymap.pop("space_type")
        region_type = keymap.pop("region_type")
        keywords = keymap.pop('keywords')

        wm = bpy.context.window_manager
        existing_kmis = get_existing_keymap_items(name)
        if wm.keyconfigs.addon:
            km = wm.keyconfigs.addon.keymaps.new(name=name, space_type=space_type)
            kmi = km.keymap_items.new(keymap_operator, letter, 'PRESS', ctrl=ctrl, alt=alt, shift=shift)
            str_vers = kmi.to_string()
            kmi.active = True
            for ekmi in existing_kmis:
                if str_vers == ekmi.to_string():
                    ekmi.active = False

            for kw, value in keywords.items():
                setattr(kmi.properties, kw, value)



            addon_keymaps.append((km, kmi))



def unregister_keymaps(addon_keymaps):
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()
