import bpy
import math

def clear_lights():
    """Remove all existing lights"""
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.context.scene.objects:
        if obj.type == 'LIGHT':
            obj.select_set(True)
    bpy.ops.object.delete()

def create_three_point_lighting(target_location=(0, 0, 1)):
    """
    Create standard three-point lighting setup
    
    Args:
        target_location: Point to aim lights at
    """
    clear_lights()
    
    # Key light (main light, 45° angle)
    bpy.ops.object.light_add(type='AREA', location=(4, -4, 5))
    key_light = bpy.context.active_object
    key_light.name = "Key_Light"
    key_light.data.energy = 200
    key_light.data.size = 3
    
    # Point at target
    direction = target_location - key_light.location
    key_light.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    
    # Fill light (soften shadows, opposite side)
    bpy.ops.object.light_add(type='AREA', location=(-4, -2, 3))
    fill_light = bpy.context.active_object
    fill_light.name = "Fill_Light"
    fill_light.data.energy = 50
    fill_light.data.size = 3
    
    # Back light (rim light, separation from background)
    bpy.ops.object.light_add(type='AREA', location=(0, 4, 4))
    back_light = bpy.context.active_object
    back_light.name = "Back_Light"
    back_light.data.energy = 75
    back_light.data.size = 2
    
    return key_light, fill_light, back_light

def create_studio_lighting():
    """Create studio lighting setup with multiple softboxes"""
    clear_lights()
    
    # Front left
    bpy.ops.object.light_add(type='AREA', location=(5, -5, 4))
    light1 = bpy.context.active_object
    light1.name = "Studio_Front_Left"
    light1.data.energy = 150
    light1.data.size = 4
    light1.rotation_euler = (math.radians(60), 0, math.radians(45))
    
    # Front right
    bpy.ops.object.light_add(type='AREA', location=(-5, -5, 4))
    light2 = bpy.context.active_object
    light2.name = "Studio_Front_Right"
    light2.data.energy = 150
    light2.data.size = 4
    light2.rotation_euler = (math.radians(60), 0, math.radians(-45))
    
    # Top
    bpy.ops.object.light_add(type='AREA', location=(0, 0, 8))
    light3 = bpy.context.active_object
    light3.name = "Studio_Top"
    light3.data.energy = 100
    light3.data.size = 5
    light3.rotation_euler = (0, 0, 0)
    
    return light1, light2, light3

def create_outdoor_lighting():
    """Create outdoor lighting with sun"""
    clear_lights()
    
    # Sun
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
    sun = bpy.context.active_object
    sun.name = "Sun"
    sun.data.energy = 3.0
    sun.rotation_euler = (math.radians(60), 0, math.radians(30))
    
    # Sky ambient (weak point light high up)
    bpy.ops.object.light_add(type='POINT', location=(0, 0, 20))
    sky = bpy.context.active_object
    sky.name = "Sky_Ambient"
    sky.data.energy = 500
    sky.data.color = (0.5, 0.7, 1.0)  # Blue tint
    
    return sun, sky

def create_dramatic_lighting():
    """Create dramatic single-source lighting"""
    clear_lights()
    
    # Single strong spot from side
    bpy.ops.object.light_add(type='SPOT', location=(5, 0, 3))
    spot = bpy.context.active_object
    spot.name = "Dramatic_Spot"
    spot.data.energy = 2000
    spot.data.spot_size = math.radians(60)
    spot.data.spot_blend = 0.2
    spot.rotation_euler = (math.radians(90), 0, math.radians(-90))
    
    # Very weak fill from front
    bpy.ops.object.light_add(type='AREA', location=(0, -5, 2))
    fill = bpy.context.active_object
    fill.name = "Dramatic_Fill"
    fill.data.energy = 20
    fill.data.size = 3
    
    return spot, fill

# Example usage
if __name__ == "__main__":
    from mathutils import Vector
    
    # Choose one lighting setup:
    create_three_point_lighting(Vector((0, 0, 1)))
    # create_studio_lighting()
    # create_outdoor_lighting()
    # create_dramatic_lighting()
    
    print("Lighting setup created successfully")