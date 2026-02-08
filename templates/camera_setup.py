import bpy
import math
from mathutils import Vector

def setup_camera(location=(7, -7, 5), target=(0, 0, 1), lens=50):
    """
    Set up camera with specified parameters
    
    Args:
        location: Camera position (x, y, z)
        target: Point camera looks at (x, y, z)
        lens: Focal length in mm (50 = normal, 35 = wide, 85 = portrait)
    
    Returns:
        Camera object
    """
    # Remove existing cameras
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.context.scene.objects:
        if obj.type == 'CAMERA':
            obj.select_set(True)
    bpy.ops.object.delete()
    
    # Create camera
    bpy.ops.object.camera_add(location=location)
    camera = bpy.context.active_object
    camera.name = "Camera"
    
    # Set as active camera
    bpy.context.scene.camera = camera
    
    # Point camera at target
    target_vector = Vector(target)
    direction = target_vector - Vector(location)
    camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    
    # Camera settings
    camera.data.lens = lens
    camera.data.sensor_width = 36  # Full frame sensor
    
    return camera

def setup_camera_with_dof(location, target, lens=50, f_stop=2.8):
    """
    Set up camera with depth of field
    
    Args:
        location: Camera position
        target: Focus point
        lens: Focal length
        f_stop: Aperture (lower = more blur, 2.8 = shallow, 8 = deep)
    """
    camera = setup_camera(location, target, lens)
    
    # Enable depth of field
    camera.data.dof.use_dof = True
    
    # Calculate focus distance
    focus_distance = (Vector(location) - Vector(target)).length
    camera.data.dof.focus_distance = focus_distance
    camera.data.dof.aperture_fstop = f_stop
    
    return camera

def setup_portrait_camera(subject_height=1.7):
    """
    Set up camera for portrait photography
    
    Args:
        subject_height: Height of subject in meters
    """
    # Position camera at subject eye level, medium distance
    camera_location = (3, -3, subject_height * 0.9)
    target = (0, 0, subject_height * 0.85)  # Slightly below eye level
    
    # Portrait lens (85mm equivalent)
    camera = setup_camera_with_dof(camera_location, target, lens=85, f_stop=2.8)
    
    return camera

def setup_product_camera():
    """Set up camera for product photography"""
    # Slightly above, angled down
    camera_location = (4, -4, 3)
    target = (0, 0, 0.5)
    
    # Standard lens with some DoF
    camera = setup_camera_with_dof(camera_location, target, lens=50, f_stop=5.6)
    
    return camera

def setup_wide_angle_camera():
    """Set up wide angle camera for scenes/environments"""
    camera_location = (5, -5, 3)
    target = (0, 0, 1)
    
    # Wide angle lens
    camera = setup_camera(camera_location, target, lens=24)
    
    return camera

def setup_orthographic_camera(scale=10):
    """
    Set up orthographic camera (no perspective)
    
    Args:
        scale: Orthographic scale (higher = more visible area)
    """
    # Top-down view
    camera_location = (0, 0, 10)
    target = (0, 0, 0)
    
    camera = setup_camera(camera_location, target, lens=50)
    
    # Switch to orthographic
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = scale
    
    # Point straight down
    camera.rotation_euler = (0, 0, 0)
    
    return camera

def create_camera_track_to(target_object):
    """
    Create camera that tracks an object
    
    Args:
        target_object: Object to track
    
    Returns:
        Camera with track-to constraint
    """
    camera_location = (7, -7, 5)
    
    # Create camera
    bpy.ops.object.camera_add(location=camera_location)
    camera = bpy.context.active_object
    camera.name = "Tracking_Camera"
    
    # Set as active
    bpy.context.scene.camera = camera
    
    # Add track-to constraint
    constraint = camera.constraints.new(type='TRACK_TO')
    constraint.target = target_object
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'
    
    return camera

def animate_camera_orbit(center=(0, 0, 1), radius=7, height=5, start_frame=1, end_frame=120):
    """
    Create camera that orbits around a point
    
    Args:
        center: Point to orbit around
        radius: Orbit radius
        height: Camera height
        start_frame: Start frame
        end_frame: End frame
    """
    # Create camera
    bpy.ops.object.camera_add(location=(radius, 0, height))
    camera = bpy.context.active_object
    camera.name = "Orbiting_Camera"
    
    # Set as active
    bpy.context.scene.camera = camera
    
    # Create empty at center for tracking
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=center)
    empty = bpy.context.active_object
    empty.name = "Orbit_Center"
    
    # Parent camera to empty
    camera.parent = empty
    camera.location = (radius, 0, height - center[2])
    
    # Point camera at center
    constraint = camera.constraints.new(type='TRACK_TO')
    constraint.target = empty
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'
    
    # Animate empty rotation
    empty.rotation_euler = (0, 0, 0)
    empty.keyframe_insert(data_path="rotation_euler", frame=start_frame)
    
    empty.rotation_euler = (0, 0, math.radians(360))
    empty.keyframe_insert(data_path="rotation_euler", frame=end_frame)
    
    return camera, empty

# Example usage
if __name__ == "__main__":
    # Choose camera setup:
    
    # Standard camera
    camera = setup_camera(location=(7, -7, 5), target=(0, 0, 1), lens=50)
    
    # OR portrait camera
    # camera = setup_portrait_camera(subject_height=1.7)
    
    # OR product camera
    # camera = setup_product_camera()
    
    # OR wide angle
    # camera = setup_wide_angle_camera()
    
    # OR orthographic
    # camera = setup_orthographic_camera(scale=10)
    
    print("Camera setup created successfully")
