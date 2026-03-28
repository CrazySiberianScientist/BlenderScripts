bl_info = {
    "name": "Measure Utils",
    "author": "ChatGPT",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > N Panel > Measure",
    "description": "Measure edge length or distance between vertices and copy result",
    "category": "Mesh",
}

import bpy
import bmesh
from mathutils import Vector


def get_measure(context):
    obj = context.edit_object
    bm = bmesh.from_edit_mesh(obj.data)

    selected_verts = [v for v in bm.verts if v.select]
    selected_edges = [e for e in bm.edges if e.select]

    # 2 verts → distance
    if len(selected_verts) == 2:
        v1, v2 = selected_verts
        return (v1.co - v2.co).length

    # edges → sum length
    elif selected_edges:
        length = 0
        for e in selected_edges:
            v1, v2 = e.verts
            length += (v1.co - v2.co).length
        return length

    return None


class MESH_OT_measure_copy(bpy.types.Operator):
    bl_idname = "mesh.measure_copy"
    bl_label = "Measure & Copy"

    def execute(self, context):
        value = get_measure(context)

        if value is None:
            self.report({'WARNING'}, "Select 2 verts or edges")
            return {'CANCELLED'}

        # учитываем scale объекта
        obj = context.edit_object
        scale = obj.matrix_world.to_scale()
        avg_scale = sum(scale) / 3.0

        value *= avg_scale

        context.scene.measure_value = value
        context.window_manager.clipboard = str(value)

        self.report({'INFO'}, f"Copied: {value:.6f}")
        return {'FINISHED'}


class VIEW3D_PT_measure_panel(bpy.types.Panel):
    bl_label = "Measure"
    bl_idname = "VIEW3D_PT_measure_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Measure"

    def draw(self, context):
        layout = self.layout

        layout.operator("mesh.measure_copy", text="Measure & Copy")

        layout.prop(context.scene, "measure_value", text="Value")


def register():
    bpy.types.Scene.measure_value = bpy.props.FloatProperty(name="Measure Value")
    bpy.utils.register_class(MESH_OT_measure_copy)
    bpy.utils.register_class(VIEW3D_PT_measure_panel)


def unregister():
    del bpy.types.Scene.measure_value
    bpy.utils.unregister_class(MESH_OT_measure_copy)
    bpy.utils.unregister_class(VIEW3D_PT_measure_panel)


if __name__ == "__main__":
    register()