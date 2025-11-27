bl_info = {
    "name": "Y3D_Mode-Switch-Panel",
    "author": "Yousei3D",
    "version": (1, 0, 0),
    "blender": (5, 0, 0),
    "location": "Popup Menu",
    "description": "Mode switch popup with optional EditMode+ submenu",
    "category": "3D View",
}

import bpy


# ============================================================
# Addon Preferences（Nパネルのチェック ON/OFF を保持）
# ============================================================
class MTOOL_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    show_editmode_plus: bpy.props.BoolProperty(
        name="Show EditMode+",
        default=True
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "show_editmode_plus")


# ============================================================
# Blender公式に合わせた利用可能モード + アイコン
# ============================================================
def get_dynamic_modes(context):
    obj = context.object
    if obj is None:
        return []

    obj_type = obj.type

    if obj_type == 'MESH':
        return [
            ('OBJECT', 'Object Mode', 'OBJECT_DATAMODE'),
            ('EDIT', 'Edit Mode', 'EDITMODE_HLT'),
            ('SCULPT', 'Sculpt Mode', 'SCULPTMODE_HLT'),
            ('VERTEX_PAINT', 'Vertex Paint', 'VPAINT_HLT'),
            ('WEIGHT_PAINT', 'Weight Paint', 'WPAINT_HLT'),
            ('TEXTURE_PAINT', 'Texture Paint', 'TPAINT_HLT'),
        ]

    elif obj_type == 'ARMATURE':
        return [
            ('OBJECT', 'Object Mode', 'OBJECT_DATAMODE'),
            ('EDIT', 'Edit Mode', 'EDITMODE_HLT'),
            ('POSE', 'Pose Mode', 'POSE_HLT'),
        ]

    elif obj_type in {'CURVE', 'SURFACE', 'FONT', 'META'}:
        return [
            ('OBJECT', 'Object Mode', 'OBJECT_DATAMODE'),
            ('EDIT', 'Edit Mode', 'EDITMODE_HLT'),
        ]

    elif obj_type == 'GPENCIL':
        return [
            ('OBJECT', 'Object Mode', 'OBJECT_DATAMODE'),
            ('EDIT', 'Edit Mode', 'EDITMODE_HLT'),
            ('SCULPT', 'Sculpt Mode', 'SCULPTMODE_HLT'),
            ('WEIGHT_PAINT', 'Weight Paint', 'WPAINT_HLT'),
        ]

    else:
        return [
            ('OBJECT', 'Object Mode', 'OBJECT_DATAMODE'),
        ]


# ============================================================
# EditMode+ サブメニュー（Vertex / Edge / Face）
# ============================================================
class MTOOL_MT_editmode_submenu(bpy.types.Menu):
    bl_idname = "MTOOL_MT_editmode_submenu"
    bl_label = "EditMode+"

    def draw(self, context):
        layout = self.layout
        layout.operator("mtool.select_mode_exec", text="Vertex", icon='VERTEXSEL').target = 'VERT'
        layout.operator("mtool.select_mode_exec", text="Edge", icon='EDGESEL').target = 'EDGE'
        layout.operator("mtool.select_mode_exec", text="Face", icon='FACESEL').target = 'FACE'


# ============================================================
# Vertex / Edge / Face モード切り替え（EditMode自動移行）
# ============================================================
class MTOOL_OT_select_mode_exec(bpy.types.Operator):
    bl_idname = "mtool.select_mode_exec"
    bl_label = "Select Mode Exec"

    target: bpy.props.StringProperty()

    def execute(self, context):

        if context.object.mode != 'EDIT':
            try:
                bpy.ops.object.mode_set(mode='EDIT')
            except:
                self.report({'ERROR'}, "Cannot enter Edit Mode")
                return {'CANCELLED'}

        bpy.ops.mesh.select_mode(type=self.target)
        return {'FINISHED'}


# ============================================================
# Mode Switch メニュー本体（EditMode+ あり/なしを制御）
# ============================================================
class MTOOL_MT_mode_switch_menu(bpy.types.Menu):
    bl_idname = "MTOOL_MT_mode_switch_menu"
    bl_label = "Mode Switch Menu"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        prefs = bpy.context.preferences.addons[__name__].preferences

        # -------------------------
        # EditMode+ 表示 ON/OFF
        # -------------------------
        if prefs.show_editmode_plus:
            layout.menu("MTOOL_MT_editmode_submenu", text="EditMode+", icon='MENU_PANEL')
            layout.separator()

        if obj is None:
            layout.label(text="No Active Object")
            return

        current_mode = obj.mode

        # -------------------------
        # モード一覧表示
        # -------------------------
        for mode_id, mode_name, icon in get_dynamic_modes(context):

            if mode_id == current_mode:
                display_name = f" {mode_name}  ◀ Now"
            else:
                display_name = mode_name

            op = layout.operator(
                "view3d.mode_switch_exec",
                text=display_name,
                icon=icon
            )
            op.target_mode = mode_id


# ============================================================
# Mode 切り替え
# ============================================================
class VIEW3D_OT_mode_switch_exec(bpy.types.Operator):
    bl_idname = "view3d.mode_switch_exec"
    bl_label = "Mode Switch Execute"

    target_mode: bpy.props.StringProperty()

    def execute(self, context):
        bpy.ops.object.mode_set(mode=self.target_mode)
        return {'FINISHED'}


# ============================================================
# Popup を View3D 上に確実に出す（Blender 5.0対応）
# ============================================================
class VIEW3D_OT_mode_switch_open(bpy.types.Operator):
    bl_idname = "view3d.mode_switch_open"
    bl_label = "Mode Switch"

    def invoke(self, context, event):

        for area in context.window.screen.areas:
            if area.type == "VIEW_3D":
                for region in area.regions:
                    if region.type == "WINDOW":
                        with context.temp_override(area=area, region=region):
                            bpy.ops.wm.call_menu(name="MTOOL_MT_mode_switch_menu")
                        return {'FINISHED'}

        self.report({'WARNING'}, "VIEW_3D area not found")
        return {'CANCELLED'}


# ============================================================
# Nパネル（EditMode+ のオン/オフ）
# ============================================================
class VIEW3D_PT_mode_switch_panel(bpy.types.Panel):
    bl_label = "Y3D Mode Switch Panel"
    bl_idname = "VIEW3D_PT_mode_switch_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Y3D"

    def draw(self, context):
        layout = self.layout
        prefs = bpy.context.preferences.addons[__name__].preferences

        layout.prop(prefs, "show_editmode_plus")
        layout.separator(factor=0.6)

        layout.operator("view3d.mode_switch_open", text="Mode Switch Menu")


# ============================================================
# Keymap
# ============================================================
addon_keymaps = []

def register_keymap():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new("view3d.mode_switch_open", type="Q", value="PRESS")
        addon_keymaps.append((km, kmi))


def unregister_keymap():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


# ============================================================
# Register
# ============================================================
classes = (
    MTOOL_AddonPreferences,
    MTOOL_MT_mode_switch_menu,
    VIEW3D_OT_mode_switch_exec,
    VIEW3D_OT_mode_switch_open,
    MTOOL_MT_editmode_submenu,
    MTOOL_OT_select_mode_exec,
    VIEW3D_PT_mode_switch_panel,
)


def register():
    for c in classes:
        bpy.utils.register_class(c)
    register_keymap()


def unregister():
    unregister_keymap()
    for c in reversed(classes):
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
