#  ***** GPL LICENSE BLOCK *****
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#  ***** GPL LICENSE BLOCK *****
 
bl_info = {
    'name': 'Stromabnehmer-Generator',
    'author': 'Johannes',
    'version': (0, 1, 0),
    'blender': (2, 6, 3),
    'location': 'Space -> Stromabnehmer-Keyframe generieren',
    'description': 'Generiere Keyframes fuer Stromabnehmer',
    'category': 'Animation',
}
 
# To support reload properly, try to access a package var, 
# if it's there, reload everything
if "bpy" in locals():
    import imp
    if 'intersections' in locals():
        imp.reload(intersections)
    if 'vector' in locals():
        imp.reload(vector)
 
import bpy
import os
from bpy.props import *
from . import intersections
from . import vector
from math import pi, sqrt

class IncomputableException(Exception):
    pass

def len_yz(a, b):
    pos_a = a.matrix_world.to_translation()
    pos_b = b.matrix_world.to_translation()
    return sqrt((pos_a.y - pos_b.y) ** 2 + (pos_a.z - pos_b.z) ** 2)

def pos_z(a):
    return a.matrix_world.to_translation().z

def pos_yz(a):
    pos_a = a.matrix_world.to_translation()
    return vector.vector([pos_a.y, pos_a.z])

class PantographCalculator(object):
    def __init__(self):
        self.point_A = vector.vector([-1., -1.])
        self.point_B = vector.vector([-1., -1.])
        self.point_C = vector.vector([-1., -1.])
        self.point_D = vector.vector([-1., -1.])
        self.point_E = vector.vector([-1., -1.])

        self.len_AD = -1
        self.len_BC = -1
        self.len_CD = -1
        self.len_DE = -1

    def compute_d(self):
        points_D = intersections.cc_int(self.point_A, self.len_AD, self.point_E, self.len_DE)
        if len(points_D) == 2:
            self.point_D = points_D[0] if points_D[0][0] > points_D[1][0] else points_D[1]
        elif len(points_D) == 1:
            self.point_D = points_D[0]
        else:
            raise IncomputableException("Point D is not computable")

    def compute_c(self):
        points_C = intersections.cc_int(self.point_D, self.len_CD, self.point_B, self.len_BC)
        if len(points_C) == 2:
            self.point_C = points_C[0] if points_C[0][0] > points_C[1][0] else points_C[1]
        elif len(points_C) == 1:
            self.point_C = points_C[0]
        else:
            raise IncomputableException("Point C is not computable")

    def compute_angle_CDE(self):
        #point_E_mirrored = vector.vector([2 * self.point_C[0] - self.point_E[0], 2 * self.point_C[1] - self.point_E[1]])
        #ang = intersections.angle_3p(point_E_mirrored, self.point_D, self.point_C)
        ang = intersections.angle_3p(self.point_C, self.point_D, self.point_E)
        if ang is None:
            raise IncomputableException("Angle is is not computable")
        else:
            return ang

    def angle_at_A(self):
        return -intersections.angle_3p(self.point_D, self.point_A, vector.vector([self.point_A[0] + 1000, self.point_A[1]]))

    def angle_at_B(self):
        return -intersections.angle_3p(self.point_C, self.point_B, vector.vector([self.point_B[0] + 1000, self.point_B[1]]))

    def angle_at_D(self):
        return -intersections.angle_3p(self.point_E, self.point_D, self.point_A)

    def compute_xE(self, yE):
        print("computing xE, A=%s, B=%s, AD=%f, BC=%f, CD=%f, DE=%f" % (self.point_A, self.point_B, self.len_AD, self.len_BC, self.len_CD, self.len_DE))

        self.point_E[1] = yE
        best_x = 0
        best_diff = 9999

        # There might be better ways to solve this equation, but this will do for the moment
        for xE in range(-1000, 1000):
            self.point_E[0] = xE / 10.0
            try:
                self.compute_d()
                self.compute_c()
                a = self.compute_angle_CDE()
                #print("x=%f, y=%f, angle=%f deg" % (self.point_E[0], self.point_E[1], a / pi * 180.0))

                if (abs(a - self.angle_CDE) < best_diff):
                    best_diff = abs(a - self.angle_CDE)
                    best_x = self.point_E[0]

            except IncomputableException:
                #print("incomputable for x=%f" % self.point_E[0])
                pass

        if best_diff == 9999:
            raise IncomputableException("all calculations failed")

        self.point_E[0] = best_x
        self.compute_d()
        self.compute_c()

class VIEW_OT_pantogen_gen_keyframe(bpy.types.Operator):
    bl_idname = "pantogen.gen_keyframe"
    bl_description = "Stromabnehmer-Keyframe generieren"
    bl_label = "Stromabnehmer-Keyframe generieren"
    bl_options = {'REGISTER', 'UNDO'}

    obj_Unterarm = StringProperty(name='Unterarm (Ursprung = Rotationszentrum)', default="Unterarm")
    obj_Kuppelstange = StringProperty(name='Kuppelstange (Ursprung = Rotationszentrum)', default="Kuppelstange")
    obj_Oberarm = StringProperty(name='Oberarm (Ursprung = Rotationszentrum)', default="Oberarm")
    obj_An_Kuppelstange = StringProperty(name='Anbaupunkt Kuppelstange an Oberarm', default="Anbaupunkt Kuppelstange")
    obj_Ende_Kuppelstange = StringProperty(name='Endpunkt Kuppelstange', default="Endpunkt Kuppelstange")
    obj_An_Palette = StringProperty(name='Anbaupunkt Palette an Oberarm', default="Anbaupunkt Palette")
    obj_An_Schleifstueck = StringProperty(name='Anbaupunkt Oberkante Schleifstueck', default="Anbaupunkt Schleifstück")

    def set_keyframe(self, ob, data_path, array_index, frame, value):
        if ob.animation_data is None:
            ob.animation_data_create()
        if ob.animation_data.action is None:
            ob.animation_data.action = bpy.data.actions.new(
                ob.name + "Action")

        # Make sure the FCurve is present on the Action.
        fcurves = [curve for curve in ob.animation_data.action.fcurves if curve.data_path == data_path and curve.array_index == array_index]
        if len(fcurves) == 0:
            fcurve = ob.animation_data.action.fcurves.new(data_path, array_index)
        else:
            fcurve = fcurves[0]

        fcurve.keyframe_points.insert(frame, value).interpolation = 'LINEAR'

    def draw(self, context):
        layout = self.layout

        layout.row().label(VIEW_OT_pantogen_gen_keyframe.obj_Unterarm[1]["name"])
        layout.row().prop_search(self, 'obj_Unterarm', context.scene, 'objects', icon='OBJECT_DATAMODE', text="")

        layout.row().label(VIEW_OT_pantogen_gen_keyframe.obj_Kuppelstange[1]["name"])
        layout.row().prop_search(self, 'obj_Kuppelstange', context.scene, 'objects', icon='OBJECT_DATAMODE', text="")

        layout.row().label(VIEW_OT_pantogen_gen_keyframe.obj_Oberarm[1]["name"])
        layout.row().prop_search(self, 'obj_Oberarm', context.scene, 'objects', icon='OBJECT_DATAMODE', text="")
        if (self.obj_Oberarm in context.scene.objects and self.obj_Unterarm in context.scene.objects and
                context.scene.objects[self.obj_Oberarm].parent != context.scene.objects[self.obj_Unterarm]):
            layout.row().label("Parent sollte Unterarm sein", icon='ERROR')

        layout.row().label(VIEW_OT_pantogen_gen_keyframe.obj_An_Kuppelstange[1]["name"])
        layout.row().prop_search(self, 'obj_An_Kuppelstange', context.scene, 'objects', icon='OBJECT_DATAMODE', text="")
        if (self.obj_An_Kuppelstange in context.scene.objects and self.obj_Oberarm in context.scene.objects and
                context.scene.objects[self.obj_An_Kuppelstange].parent != context.scene.objects[self.obj_Oberarm]):
            layout.row().label("Parent sollte Oberarm sein", icon='ERROR')

        layout.row().label(VIEW_OT_pantogen_gen_keyframe.obj_Ende_Kuppelstange[1]["name"])
        layout.row().prop_search(self, 'obj_Ende_Kuppelstange', context.scene, 'objects', icon='OBJECT_DATAMODE', text="")
        if (self.obj_An_Kuppelstange in context.scene.objects and self.obj_Ende_Kuppelstange in context.scene.objects and
                context.scene.objects[self.obj_Ende_Kuppelstange].parent != context.scene.objects[self.obj_Kuppelstange]):
            layout.row().label("Parent sollte Kuppelstange sein", icon='ERROR')

        layout.row().label(VIEW_OT_pantogen_gen_keyframe.obj_An_Palette[1]["name"])
        layout.row().prop_search(self, 'obj_An_Palette', context.scene, 'objects', icon='OBJECT_DATAMODE', text="")
        if (self.obj_An_Palette in context.scene.objects and self.obj_Oberarm in context.scene.objects and
                context.scene.objects[self.obj_An_Palette].parent != context.scene.objects[self.obj_Oberarm]):
            layout.row().label("Parent sollte Oberarm sein", icon='ERROR')

        layout.row().label(VIEW_OT_pantogen_gen_keyframe.obj_An_Schleifstueck[1]["name"])
        layout.row().prop_search(self, 'obj_An_Schleifstueck', context.scene, 'objects', icon='OBJECT_DATAMODE', text="")
        if (self.obj_An_Palette in context.scene.objects and self.obj_An_Schleifstueck in context.scene.objects and
                context.scene.objects[self.obj_An_Schleifstueck].parent != context.scene.objects[self.obj_An_Palette]):
            layout.row().label("Parent sollte Anbaupunkt Palette sein", icon='ERROR')

    def execute(self, context):
        for o in (self.obj_Oberarm, self.obj_Unterarm, self.obj_Kuppelstange, self.obj_An_Schleifstueck,
                self.obj_An_Palette, self.obj_An_Kuppelstange, self.obj_Ende_Kuppelstange):
            if o not in context.scene.objects:
                return {'FINISHED'}

        obj_Unterarm = context.scene.objects[self.obj_Unterarm]               # A
        obj_Kuppelstange = context.scene.objects[self.obj_Kuppelstange]       # B
        obj_Oberarm = context.scene.objects[self.obj_Oberarm]                 # D
        obj_An_Kuppelstange = context.scene.objects[self.obj_An_Kuppelstange] # C
        obj_Ende_Kuppelstange = context.scene.objects[self.obj_Ende_Kuppelstange] # C
        obj_An_Palette = context.scene.objects[self.obj_An_Palette]           # E
        obj_An_Schleifstueck = context.scene.objects[self.obj_An_Schleifstueck]

        c = PantographCalculator()
        c.point_A = 100 * pos_yz(obj_Unterarm)
        c.point_B = 100 * pos_yz(obj_Kuppelstange)

        c.len_AD = 100 * len_yz(obj_Unterarm, obj_Oberarm)
        c.len_BC = 100 * len_yz(obj_Kuppelstange, obj_Ende_Kuppelstange)
        c.len_CD = 100 * len_yz(obj_An_Kuppelstange, obj_Oberarm)
        c.len_DE = 100 * len_yz(obj_Oberarm, obj_An_Palette)

        c.angle_CDE = intersections.angle_3p(100 * pos_yz(obj_An_Kuppelstange), 100 * pos_yz(obj_Oberarm), 100 * pos_yz(obj_An_Palette))
        print("angle_CDE = %f deg" % (c.angle_CDE / pi * 180.0))

        off_Schleifstueck = 100 * (pos_z(obj_An_Schleifstueck) - pos_z(obj_An_Palette))

        startframe = context.scene.frame_start
        endframe = context.scene.frame_end
        curframe = context.scene.frame_current
        height = 2.5 * 100 * float(curframe - startframe) / float(endframe - startframe)

        c.compute_xE(height - off_Schleifstueck)
       
        if False:
            import mathutils
            empty = bpy.data.objects.new("A", None)
            empty.location = mathutils.Vector([0, c.point_A[0], c.point_A[1]])
            context.scene.objects.link(empty)
            empty = bpy.data.objects.new("B", None)
            empty.location = mathutils.Vector([0, c.point_B[0], c.point_B[1]])
            context.scene.objects.link(empty)
            empty = bpy.data.objects.new("C", None)
            empty.location = mathutils.Vector([0, c.point_C[0], c.point_C[1]])
            context.scene.objects.link(empty)
            empty = bpy.data.objects.new("D", None)
            empty.location = mathutils.Vector([0, c.point_D[0], c.point_D[1]])
            context.scene.objects.link(empty)
            empty = bpy.data.objects.new("E", None)
            empty.location = mathutils.Vector([0, c.point_E[0], c.point_E[1]])
            context.scene.objects.link(empty)

        self.set_keyframe(obj_Unterarm, "rotation_euler", 0, curframe, c.angle_at_A())
        self.set_keyframe(obj_Kuppelstange, "rotation_euler", 0, curframe, c.angle_at_B())
        self.set_keyframe(obj_Oberarm, "rotation_euler", 0, curframe, c.angle_at_D() + pi)

        context.scene.frame_set(curframe)

        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
 
def register():
    bpy.utils.register_module(__name__)
 
def unregister():
    bpy.utils.unregister_module(__name__)
 
if __name__ == "__main__":
    register()
