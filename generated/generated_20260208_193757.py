import bpy
import math

# Create a new collection for lights
collection = bpy.data.collections.new("Lights")
bpy.context.scene.collection.children.link(collection)

# Add an area light (soft glow) from the side
bpy.ops.object.light_add(type='AREA', location=(4, -2, 3))
light = bpy.context.active_object
light.data.energy = 200
light.rotation_euler = (math.radians(45), 0, math.radians(45))

# Add a point light (shadow) from the top
bpy.ops.object.light_add(type='POINT', location=(0, 2, 5))
shadow_light = bpy.context.active_object
shadow_light.data.energy = 1000
shadow_light.data.shadow_soft_size = 1.0

# Link lights to collection
collection.objects.link(light)
collection.objects.link(shadow_light)

# Add a camera
bpy.ops.object.camera_add(location=(7, -2, 5))
camera = bpy.context.active_object

# Set as active camera
bpy.context.scene.camera = camera

# Point at origin
direction = Vector((0, 0, 0)) - camera.location
camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

# Camera settings
camera.data.lens = 50  # Focal length in mm
camera.data.sensor_width = 36  # Sensor size
camera.data.dof.use_dof = False  # Depth of field

# Set up a simple wooden table
bpy.ops.mesh.primitive_cube_add(size=5, location=(0, -2, 0))
table = bpy.context.active_object
table.name = "Table"
table.data.materials.append(bpy.data.materials.new(name="Wood"))
bpy.context.object.data.materials[0].diffuse_color = (0.7, 0.4, 0.1)

# Add a vase and flower
bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=2, location=(0, -3, 0))
vase = bpy.context.active_object
vase.name = "Vase"
vase.data.materials.append(bpy.data.materials.new(name="Ceramic"))
bpy.context.object.data.materials[0].diffuse_color = (0.9, 0.8, 0.7)

# Add a simple concrete wall background
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, -2, 5))
wall = bpy.context.active_object
wall.name = "Wall"
wall.data.materials.append(bpy.data.materials.new(name="Concrete"))
bpy.context.object.data.materials[0].diffuse_color = (0.4, 0.3, 0.2)

# Set render settings
scene = bpy.context.scene

# Resolution
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100

# Render engine
scene.render.engine = 'CYCLES'  # or 'BLENDER_EEVEE'

# Cycles settings
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPENIMAGEDENOISE'

# Output
scene.render.filepath = "/tmp/render.png"
scene.render.image_settings.file_format = 'PNG'