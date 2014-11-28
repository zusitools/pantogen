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

def len_yz(a, b):
    pos_a = a.matrix_world.to_translation()
    pos_b = b.matrix_world.to_translation()
    return sqrt((pos_a.y - pos_b.y) ** 2 + (pos_a.z - pos_b.z) ** 2)

def pos_z(a):
    return a.matrix_world.to_translation().z

def pos_yz(a):
    pos_a = a.matrix_world.to_translation()
    return vector.vector([pos_a.y, pos_a.z])

class VIEW_OT_pantogen_gen_keyframe(bpy.types.Operator):
    bl_idname = "pantogen.gen_keyframe"
    bl_description = "Stromabnehmer-Keyframe generieren"
    bl_label = "Stromabnehmer-Keyframe generieren"
    bl_options = {'REGISTER', 'UNDO'}

    obj_Unterarm = StringProperty(name='Unterarm (Ursprung = Rotationszentrum)', default="Unterarm")
    obj_Kuppelstange = StringProperty(name='Kuppelstange (Ursprung = Rotationszentrum)', default="Kuppelstange")
    obj_Oberarm = StringProperty(name='Oberarm (Ursprung = Rotationszentrum)', default="Oberarm")
    obj_An_Kuppelstange = StringProperty(name='Anbaupunkt Kuppelstange an Oberarm', default="Anbaupunkt Kuppelstange")
    obj_An_Palette = StringProperty(name='Anbaupunkt Palette an Oberarm', default="Anbaupunkt Palette")
    obj_Schleifstueck = StringProperty(name='Oberkante Schleifstueck', default="Schleifstück")

    def draw(self, context):
        layout = self.layout

        layout.row().label(VIEW_OT_pantogen_gen_keyframe.obj_Unterarm[1]["name"])
        layout.row().prop_search(self, 'obj_Unterarm', context.scene, 'objects', icon='OBJECT_DATAMODE', text="")
        layout.row().label(VIEW_OT_pantogen_gen_keyframe.obj_Kuppelstange[1]["name"])
        layout.row().prop_search(self, 'obj_Kuppelstange', context.scene, 'objects', icon='OBJECT_DATAMODE', text="")
        layout.row().label(VIEW_OT_pantogen_gen_keyframe.obj_Oberarm[1]["name"])
        layout.row().prop_search(self, 'obj_Oberarm', context.scene, 'objects', icon='OBJECT_DATAMODE', text="")
        layout.row().label(VIEW_OT_pantogen_gen_keyframe.obj_An_Kuppelstange[1]["name"])
        layout.row().prop_search(self, 'obj_An_Kuppelstange', context.scene, 'objects', icon='OBJECT_DATAMODE', text="")
        layout.row().label(VIEW_OT_pantogen_gen_keyframe.obj_An_Palette[1]["name"])
        layout.row().prop_search(self, 'obj_An_Palette', context.scene, 'objects', icon='OBJECT_DATAMODE', text="")
        layout.row().label(VIEW_OT_pantogen_gen_keyframe.obj_Schleifstueck[1]["name"])
        layout.row().prop_search(self, 'obj_Schleifstueck', context.scene, 'objects', icon='OBJECT_DATAMODE', text="")

    def execute(self, context):
        for o in (self.obj_Oberarm, self.obj_Unterarm, self.obj_Kuppelstange, self.obj_Schleifstueck, self.obj_An_Palette, self.obj_An_Kuppelstange):
            if o not in context.scene.objects:
                return {'FINISHED'}

        obj_Unterarm = context.scene.objects[self.obj_Unterarm]
        obj_Kuppelstange = context.scene.objects[self.obj_Kuppelstange]
        obj_Oberarm = context.scene.objects[self.obj_Oberarm]
        obj_An_Kuppelstange = context.scene.objects[self.obj_An_Kuppelstange]
        obj_An_Palette = context.scene.objects[self.obj_An_Palette]
        obj_Schleifstueck = context.scene.objects[self.obj_Schleifstueck]

        if (obj_An_Kuppelstange.parent != obj_Oberarm or
                obj_An_Palette.parent != obj_Oberarm or
                obj_Oberarm.parent != obj_Unterarm):
            return {'FINISHED'}

        point_A = pos_yz(obj_Unterarm)
        point_B = pos_yz(obj_Kuppelstange)

        len_AD = len_yz(obj_Unterarm, obj_Oberarm)
        len_BC = len_yz(obj_Kuppelstange, obj_An_Kuppelstange)
        len_CD = len_yz(obj_An_Kuppelstange, obj_Oberarm)
        len_DE = len_yz(obj_Oberarm, obj_An_Palette)

        angle_CDE = intersections.angle_3p(pos_yz(obj_An_Kuppelstange), pos_yz(obj_Oberarm), pos_yz(obj_An_Palette))

        off_Schleifstueck = pos_z(obj_Schleifstueck) - pos_z(obj_An_Palette)

        print("A=%s, B=%s, AD=%f, BC=%f, CD=%f, DE=%f, CDE=%f, offset=%f" % (str(point_A), str(point_B), len_AD, len_BC, len_CD, len_DE, angle_CDE, off_Schleifstueck))

        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
 
def register():
    bpy.utils.register_module(__name__)
 
def unregister():
    bpy.utils.unregister_module(__name__)
 
if __name__ == "__main__":
    register()
