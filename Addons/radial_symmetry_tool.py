bl_info = {
    "name": "Radial Symmetry Tool",
    "author": "Developer",
    "version": (0, 1, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > Tool",
    "description": "Select vertices by radial symmetry and batch assign to vertex groups",
    "category": "Mesh",
}

import bpy
from bpy.props import EnumProperty, FloatProperty, IntProperty, StringProperty
from bpy.types import Panel, Operator
import math


class MESH_OT_select_radial_symmetry(Operator):
    bl_idname = "mesh.select_radial_symmetry"
    bl_label = "Select Radial Symmetry"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = context.active_object
        
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Select a mesh object")
            return {'CANCELLED'}
        
        if obj.mode != 'EDIT':
            self.report({'ERROR'}, "Enter Edit Mode")
            return {'CANCELLED'}
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        mesh = obj.data
        axis = context.scene.radial_axis
        number = context.scene.radial_divisions
        tol = context.scene.radial_tolerance
        
        selected = [v for v in mesh.vertices if v.select]
        
        if not selected:
            self.report({'WARNING'}, "No vertices selected")
            bpy.ops.object.mode_set(mode='EDIT')
            return {'CANCELLED'}
        
        axis_map = {'X': (1, 2), 'Y': (0, 2), 'Z': (0, 1)}
        axis_idx_main = {'X': 0, 'Y': 1, 'Z': 2}[axis]
        u, v = axis_map[axis]
        
        angle_step = 2 * math.pi / number
        
        # Упорядоченный список выделенных вершин
        ordered_selected = []
        
        found = 0
        
        for sel_v in selected:
            ordered_selected.append(sel_v.index)
            sel_pos = sel_v.co
            
            u_sel = sel_pos[u]
            v_sel = sel_pos[v]
            radius = math.sqrt(u_sel**2 + v_sel**2)
            angle_sel = math.atan2(v_sel, u_sel)
            main_coord = sel_pos[axis_idx_main]
            
            for div in range(1, number):
                target_angle = angle_sel + angle_step * div
                
                u_target = radius * math.cos(target_angle)
                v_target = radius * math.sin(target_angle)
                
                for v_mesh in mesh.vertices:
                    if v_mesh.select:
                        continue
                    
                    v_pos = v_mesh.co
                    
                    if (abs(v_pos[u] - u_target) <= tol and
                        abs(v_pos[v] - v_target) <= tol and
                        abs(v_pos[axis_idx_main] - main_coord) <= tol):
                        v_mesh.select = True
                        ordered_selected.append(v_mesh.index)
                        found += 1
                        break
        
        # Сохраняем порядок вершин в свойство сцены
        context.scene.radial_selected_order = ','.join(map(str, ordered_selected))
        
        bpy.ops.object.mode_set(mode='EDIT')
        
        self.report({'INFO'}, f"Selected {found} vertices")
        return {'FINISHED'}


class MESH_OT_assign_radial_vertex_group(Operator):
    bl_idname = "mesh.assign_radial_vertex_group"
    bl_label = "Assign Radial to Vertex Groups"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = context.active_object
        
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Select mesh object")
            return {'CANCELLED'}
        
        if obj.mode != 'EDIT':
            self.report({'ERROR'}, "Enter Edit Mode")
            return {'CANCELLED'}
        
        prefix = context.scene.radial_prefix
        divisions = context.scene.radial_divisions
        postfix = context.scene.radial_postfix
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Используем сохранённый порядок или текущее выделение
        if context.scene.radial_selected_order:
            selected = [int(i) for i in context.scene.radial_selected_order.split(',') if i]
        else:
            selected = [v.index for v in obj.data.vertices if v.select]
        
        # Применяем направление обхода
        if context.scene.radial_order_direction == 'REVERSE':
            selected = selected[::-1]
        
        if len(selected) % divisions != 0:
            self.report({'ERROR'}, f"Selected {len(selected)} vertices must divide evenly by {divisions}")
            bpy.ops.object.mode_set(mode='EDIT')
            return {'CANCELLED'}
        
        if not selected:
            self.report({'ERROR'}, "No vertices selected")
            bpy.ops.object.mode_set(mode='EDIT')
            return {'CANCELLED'}
        
        group_size = len(selected) // divisions
        weight = context.scene.radial_vertex_weight
        
        for div_idx in range(divisions):
            group_name = f"{prefix}{div_idx}{postfix}"
            
            if group_name not in obj.vertex_groups:
                vgroup = obj.vertex_groups.new(name=group_name)
            else:
                vgroup = obj.vertex_groups[group_name]
            
            start_idx = div_idx * group_size
            end_idx = start_idx + group_size
            group_vertices = selected[start_idx:end_idx]
            
            for vert_idx in group_vertices:
                vgroup.add([vert_idx], weight, 'REPLACE')
        
        bpy.ops.object.mode_set(mode='EDIT')
        
        self.report({'INFO'}, f"Divided {len(selected)} vertices into {divisions} groups")
        return {'FINISHED'}


class MESH_OT_radial_select_and_assign(Operator):
    bl_idname = "mesh.radial_select_and_assign"
    bl_label = "Select Symmetry & Assign"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = context.active_object
        
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Select a mesh object")
            return {'CANCELLED'}
        
        if obj.mode != 'EDIT':
            self.report({'ERROR'}, "Enter Edit Mode")
            return {'CANCELLED'}
        
        # Шаг 1: Выделение по радиальной симметрии с сохранением порядка
        bpy.ops.object.mode_set(mode='OBJECT')
        
        mesh = obj.data
        axis = context.scene.radial_axis
        number = context.scene.radial_divisions
        tol = context.scene.radial_tolerance
        
        selected_initial = [v for v in mesh.vertices if v.select]
        
        if not selected_initial:
            self.report({'WARNING'}, "No vertices selected")
            bpy.ops.object.mode_set(mode='EDIT')
            return {'CANCELLED'}
        
        axis_map = {'X': (1, 2), 'Y': (0, 2), 'Z': (0, 1)}
        axis_idx_main = {'X': 0, 'Y': 1, 'Z': 2}[axis]
        u, v = axis_map[axis]
        
        angle_step = 2 * math.pi / number
        
        # Упорядоченный список выделенных вершин в порядке выделения
        ordered_selected = []
        
        # Шаг 1: добавляем все исходные вершины
        for sel_v in selected_initial:
            ordered_selected.append(sel_v.index)
            context.scene.radial_selected_order = ','.join(map(str, ordered_selected))
        
        # Шаг 2: для каждого деления ищем соответствующие вершины
        for div in range(1, number):
            for sel_v in selected_initial:
                sel_pos = sel_v.co
                
                u_sel = sel_pos[u]
                v_sel = sel_pos[v]
                radius = math.sqrt(u_sel**2 + v_sel**2)
                angle_sel = math.atan2(v_sel, u_sel)
                main_coord = sel_pos[axis_idx_main]
                
                target_angle = angle_sel + angle_step * div
                
                u_target = radius * math.cos(target_angle)
                v_target = radius * math.sin(target_angle)
                
                for v_mesh in mesh.vertices:
                    if v_mesh.select:
                        continue
                    
                    v_pos = v_mesh.co
                    
                    if (abs(v_pos[u] - u_target) <= tol and
                        abs(v_pos[v] - v_target) <= tol and
                        abs(v_pos[axis_idx_main] - main_coord) <= tol):
                        v_mesh.select = True
                        ordered_selected.append(v_mesh.index)
                        context.scene.radial_selected_order = ','.join(map(str, ordered_selected))
                        break
        
        # Шаг 2: Присваивание в vertex groups в порядке выделения
        prefix = context.scene.radial_prefix
        divisions = context.scene.radial_divisions
        postfix = context.scene.radial_postfix
        
        # Применяем направление обхода
        if context.scene.radial_order_direction == 'REVERSE':
            ordered_selected = ordered_selected[::-1]
        
        if len(ordered_selected) % divisions != 0:
            self.report({'ERROR'}, f"Selected {len(ordered_selected)} vertices must divide evenly by {divisions}")
            bpy.ops.object.mode_set(mode='EDIT')
            return {'CANCELLED'}
        
        group_size = len(ordered_selected) // divisions
        weight = context.scene.radial_vertex_weight
        
        for div_idx in range(divisions):
            group_name = f"{prefix}{div_idx}{postfix}"
            
            if group_name not in obj.vertex_groups:
                vgroup = obj.vertex_groups.new(name=group_name)
            else:
                vgroup = obj.vertex_groups[group_name]
            
            start_idx = div_idx * group_size
            end_idx = start_idx + group_size
            group_vertices = ordered_selected[start_idx:end_idx]
            
            for vert_idx in group_vertices:
                vgroup.add([vert_idx], weight, 'REPLACE')
        
        bpy.ops.object.mode_set(mode='EDIT')
        
        self.report({'INFO'}, f"Selected and divided {len(ordered_selected)} vertices into {divisions} groups")
        return {'FINISHED'}


class MESH_PT_radial_symmetry(Panel):
    bl_label = "Radial Symmetry Tool"
    bl_idname = "MESH_PT_radial_symmetry"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"
    
    @classmethod
    def poll(cls, context):
        return (context.active_object is not None and
                context.active_object.type == 'MESH' and
                context.active_object.mode == 'EDIT')
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.active_object
        
        # Radial Symmetry Parameters
        box1 = layout.box()
        box1.label(text="Radial Symmetry")
        col1 = box1.column(align=True)
        col1.prop(scene, "radial_axis", text="Axis")
        col1.prop(scene, "radial_divisions", text="Divisions")
        col1.prop(scene, "radial_tolerance", text="Tolerance")
        
        # Vertex Group Settings
        box2 = layout.box()
        box2.label(text="Vertex Group Settings")
        col2 = box2.column(align=True)
        col2.prop(scene, "radial_prefix", text="Prefix")
        col2.prop(scene, "radial_postfix", text="Postfix")
        col2.prop(scene, "radial_vertex_weight", text="Weight", slider=True)
        col2.prop(scene, "radial_order_direction", text="Order")
        
        # Operations
        box3 = layout.box()
        box3.label(text="Operations")
        col3 = box3.column(align=True)
        col3.operator("mesh.select_radial_symmetry", text="Select by Symmetry")
        col3.operator("mesh.assign_radial_vertex_group", text="Assign to Groups")
        col3.operator("mesh.radial_select_and_assign", text="Select & Assign")
        
        # Existing Groups
        box4 = layout.box()
        box4.label(text="Existing Groups")
        if obj.vertex_groups:
            col4 = box4.column(align=False)
            for vgroup in obj.vertex_groups:
                vert_count = 0
                for v in obj.data.vertices:
                    try:
                        if vgroup.weight(v.index) > 0:
                            vert_count += 1
                    except RuntimeError:
                        pass
                
                row = col4.row(align=True)
                row.label(text=f"{vgroup.name}")
                row.label(text=f"({vert_count})")
        else:
            box4.label(text="No groups created")


def register():
    bpy.utils.register_class(MESH_OT_select_radial_symmetry)
    bpy.utils.register_class(MESH_OT_assign_radial_vertex_group)
    bpy.utils.register_class(MESH_OT_radial_select_and_assign)
    bpy.utils.register_class(MESH_PT_radial_symmetry)
    
    bpy.types.Scene.radial_axis = EnumProperty(
        name="Radial Axis",
        items=[('X', "X", ""), ('Y', "Y", ""), ('Z', "Z", "")],
        default='X'
    )
    
    bpy.types.Scene.radial_divisions = IntProperty(
        name="Radial Divisions",
        default=3,
        min=2,
        max=32
    )
    
    bpy.types.Scene.radial_tolerance = FloatProperty(
        name="Radial Tolerance",
        default=0.001,
        min=0.0001,
        max=1.0
    )
    
    bpy.types.Scene.radial_prefix = StringProperty(
        name="Prefix",
        default=""
    )
    
    bpy.types.Scene.radial_postfix = StringProperty(
        name="Postfix",
        default=""
    )
    
    bpy.types.Scene.radial_selected_order = StringProperty(
        name="Radial Selected Order",
        default="",
        description="Internal: stores the order of selected vertices"
    )
    
    bpy.types.Scene.radial_vertex_weight = FloatProperty(
        name="Vertex Weight",
        default=1.0,
        min=0.0,
        max=1.0,
        description="Weight value for vertices when assigning to groups"
    )
    
    bpy.types.Scene.radial_order_direction = EnumProperty(
        name="Order Direction",
        items=[('FORWARD', "Forward", "Process vertices in forward order"),
               ('REVERSE', "Reverse", "Process vertices in reverse order")],
        default='FORWARD',
        description="Direction of processing vertices for group assignment"
    )


def unregister():
    bpy.utils.unregister_class(MESH_OT_select_radial_symmetry)
    bpy.utils.unregister_class(MESH_OT_assign_radial_vertex_group)
    bpy.utils.unregister_class(MESH_OT_radial_select_and_assign)
    bpy.utils.unregister_class(MESH_PT_radial_symmetry)
    
    if hasattr(bpy.types.Scene, "radial_axis"):
        del bpy.types.Scene.radial_axis
    if hasattr(bpy.types.Scene, "radial_divisions"):
        del bpy.types.Scene.radial_divisions
    if hasattr(bpy.types.Scene, "radial_tolerance"):
        del bpy.types.Scene.radial_tolerance
    if hasattr(bpy.types.Scene, "radial_prefix"):
        del bpy.types.Scene.radial_prefix
    if hasattr(bpy.types.Scene, "radial_postfix"):
        del bpy.types.Scene.radial_postfix
    if hasattr(bpy.types.Scene, "radial_selected_order"):
        del bpy.types.Scene.radial_selected_order
    if hasattr(bpy.types.Scene, "radial_vertex_weight"):
        del bpy.types.Scene.radial_vertex_weight
    if hasattr(bpy.types.Scene, "radial_order_direction"):
        del bpy.types.Scene.radial_order_direction


if __name__ == "__main__":
    register()
