import struct
import math 
import bpy
import mathutils as mt
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, EnumProperty
from bpy.types import Operator


bl_info = {
	"name": "GLrawd (.rawd)",
	"author": "Goran Milovanovic",
	"blender": (2, 6, 3),
	"location": "File > Import-Export",
	"description": "Export scene data, in a binary format, which can be consumed directly by OpenGL.",
	"wiki_url": "http://www.github.com/goranm/GLrawd",
	"support": 'COMMUNITY',
	"category": "Import-Export"
}

def export(context, filepath, mode):

	if mode == "Selected":
		objects = context.selected_objects
	else:
		objects = bpy.data.objects

	objects = [obj for obj in objects if obj.type == "MESH"] # Only objects with a mesh

	meshes = set( (obj.data for obj in objects) ) # Only unique meshes


	f = open(filepath, "wb")


	# Base verts
	# -----------------------------------------------------------------

	count_vertices = sum( (len(mesh.vertices) for mesh in meshes) )

	f.write( struct.pack('I', count_vertices) )

	idx_vertices = 0

	for mesh in meshes:

		mesh["idx_vertices"] = idx_vertices

		for v in mesh.vertices:
			vec = v.co

			for n in vec:
				f.write( struct.pack('f', n) )

		idx_vertices += len(mesh.vertices)
	


	# Indices
	# -----------------------------------------------------------------

	isTriangle = lambda p: True if len(p.vertices) < 4 else False

	count_indices = sum( sum((3 if isTriangle(poly) else 6 for poly in mesh.polygons)) \
				for mesh in meshes )

	f.write( struct.pack('I', count_indices) )


	idx_indices = 0

	for mesh in meshes:

		mesh["idx_indices"] = idx_indices

		count_idx = 0

		for poly in mesh.polygons:

			if isTriangle(poly):
				vert_indices = poly.vertices
			else:
				vert_indices = [poly.vertices[i] for i in (0, 1, 2, 2, 3, 0)]

			for i in vert_indices:
				f.write( struct.pack('I', mesh["idx_vertices"] + i) )

			count_idx += len(vert_indices)

		idx_indices += count_idx

		mesh["count_idx"] = count_idx


	# Objects
	# -----------------------------------------------------------------

	f.write( struct.pack('I', len(objects)) )

	mat_rot = mt.Matrix.Rotation(-math.pi/2, 4, 'X')

	for obj in objects:

		# Write matrix

		mat_world = mat_rot * obj.matrix_world

		for vec in mat_world.col:

			for n in vec:
				f.write( struct.pack('f', n) )


		# Write index offset

		mesh = obj.data
		f.write( struct.pack('I', mesh["idx_indices"]) )


		# Write index count

		f.write( struct.pack('I', mesh["count_idx"]) )


	return {'FINISHED'}


class ExportRawd(Operator, ExportHelper):
	"""Export to GLrawd format (.rawd)"""
	bl_idname = "export_scene.rawd"
	bl_label = "Export to .rawd"

	filename_ext = ".rawd"

	filter_glob = StringProperty(
			default="*.rawd",
			options={'HIDDEN'},
			)

	mode = EnumProperty(
			name="Export",
			description="",
			items=(
				("All", "All", "Export all objects."),
				("Selected", "Selected", "Export selected objects.")),
			default='All',
			)

	def execute(self, context):
		return export(context, self.filepath, self.mode)


def menu_func_export(self, context):
	self.layout.operator(ExportRawd.bl_idname, text="GLrawd (.rawd)")


def register():
	bpy.utils.register_class(ExportRawd)
	bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
	bpy.utils.unregister_class(ExportRawd)
	bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
	register()
