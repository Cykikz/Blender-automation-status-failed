import bpy

# Set location (0, 0, 0) for the cube
location = (0, 0, 0)

# Create a new cube object with size 1 meter
bpy.ops.mesh.primitive_cube_add(size=1, location=location)

# Get the newly created cube object
cube = bpy.context.active_object

# Set the color of the cube to red
cube.data.materials.append(bpy.data.materials.new("RedMaterial"))
cube.data.materials[0].diffuse_color = (1.0, 0.0, 0.0)

# Set a descriptive name for the cube object
cube.name = "RedCube"

# Save the scene to file (optional)
bpy.ops.wm.save_mainfile(filepath="red_cube.blend")

import bpy

# Save
bpy.ops.wm.save_as_mainfile(filepath=r"E:\Cykikkdata\Cykikk[Projects,miscellaneous]\Datascience , AI ML Projects\Blenderaiautomation\blender-ai-automation\output\blend_files\scene_20260208_192305.blend")
print(f"Saved to: E:\Cykikkdata\Cykikk[Projects,miscellaneous]\Datascience , AI ML Projects\Blenderaiautomation\blender-ai-automation\output\blend_files\scene_20260208_192305.blend")
