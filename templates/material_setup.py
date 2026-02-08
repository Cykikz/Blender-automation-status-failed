import bpy

def create_metal_material(name="Metal", color=(0.8, 0.8, 0.8, 1.0), roughness=0.2):
    """Create a metallic material"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    
    bsdf = nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = roughness
    
    return mat

def create_glass_material(name="Glass", ior=1.45):
    """Create a glass material"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    
    bsdf = nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (1.0, 1.0, 1.0, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Roughness'].default_value = 0.0
    bsdf.inputs['Transmission'].default_value = 1.0
    bsdf.inputs['IOR'].default_value = ior
    
    return mat

def create_emission_material(name="Emission", color=(1.0, 1.0, 1.0, 1.0), strength=5.0):
    """Create an emission (glowing) material"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    
    bsdf = nodes["Principled BSDF"]
    bsdf.inputs['Emission'].default_value = color
    bsdf.inputs['Emission Strength'].default_value = strength
    
    return mat

def create_plastic_material(name="Plastic", color=(0.8, 0.1, 0.1, 1.0)):
    """Create a plastic material"""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    
    bsdf = nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Roughness'].default_value = 0.3
    bsdf.inputs['Specular'].default_value = 0.5
    
    return mat

# Example usage:
if __name__ == "__main__":
    # Create example materials
    gold = create_metal_material("Gold", (1.0, 0.766, 0.336, 1.0), 0.2)
    glass = create_glass_material("Glass", 1.45)
    glow = create_emission_material("Glow", (0.2, 0.5, 1.0, 1.0), 10.0)
    red_plastic = create_plastic_material("RedPlastic", (0.8, 0.1, 0.1, 1.0))
    
    print("Materials created successfully")