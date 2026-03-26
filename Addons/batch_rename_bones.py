bl_info = {
    "name": "Bone & Vertex Group Batch Rename (Selected Bones Only)",
    "author": "ChatGPT",
    "version": (1, 1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Tool",
    "description": "Batch rename selected bones and matching vertex groups",
    "category": "Rigging",
}

import bpy


# ------------------------
# Properties
# ------------------------
class BBR_Properties(bpy.types.PropertyGroup):
    prefix: bpy.props.StringProperty(
        name="Prefix",
        description="Prefix for new names",
        default="Prefix"
    )


# ------------------------
# Operator
# ------------------------
class BBR_OT_Rename(bpy.types.Operator):
    bl_idname = "bbr.rename"
    bl_label = "Rename Selected Bones & VGroups"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.bbr_props
        new_prefix = props.prefix

        obj = context.active_object

        if not obj or obj.type != 'ARMATURE':
            self.report({'WARNING'}, "Select an armature")
            return {'CANCELLED'}

        if context.mode != 'POSE':
            self.report({'WARNING'}, "Switch to Pose Mode and select bones")
            return {'CANCELLED'}

        selected_bones = context.selected_pose_bones

        if not selected_bones:
            self.report({'WARNING'}, "No bones selected")
            return {'CANCELLED'}

        index = 0
        renamed_count = 0

        # Получаем меши, привязанные к армейчуре
        meshes = [child for child in obj.children if child.type == 'MESH']

        for bone in selected_bones:
            old_name = bone.name
            new_name = f"{new_prefix}.{index:03d}"

            # Переименование кости
            bone.name = new_name

            # Переименование vertex groups во всех мешах
            for mesh in meshes:
                vg = mesh.vertex_groups.get(old_name)
                if vg:
                    vg.name = new_name
                    renamed_count += 1

            index += 1

        self.report({'INFO'}, f"Renamed {index} bones and {renamed_count} vertex groups")
        return {'FINISHED'}


# ------------------------
# UI Panel
# ------------------------
class BBR_PT_Panel(bpy.types.Panel):
    bl_label = "Bone Batch Rename"
    bl_idname = "BBR_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"

    def draw(self, context):
        layout = self.layout
        props = context.scene.bbr_props

        layout.prop(props, "prefix")
        layout.operator("bbr.rename", icon='ARMATURE_DATA')


# ------------------------
# Registration
# ------------------------
classes = (
    BBR_Properties,
    BBR_OT_Rename,
    BBR_PT_Panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bbr_props = bpy.props.PointerProperty(type=BBR_Properties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.bbr_props


if __name__ == "__main__":
    register()