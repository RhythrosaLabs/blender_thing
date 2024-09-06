import bpy
import random
import math
import os

def generate_tree_color():
    # Generate vibrant colors for trees
    hue = random.uniform(0, 1)
    saturation = random.uniform(0.5, 1)
    value = random.uniform(0.5, 1)
    return hue, saturation, value

def hsv_to_rgb(h, s, v):
    # Convert HSV to RGB
    if s == 0.0:
        return (v, v, v)
    i = int(h * 6.)
    f = (h * 6.) - i
    p, q, t = v * (1. - s), v * (1. - s * f), v * (1. - s * (1. - f))
    i %= 6
    if i == 0: return (v, t, p)
    if i == 1: return (q, v, p)
    if i == 2: return (p, v, t)
    if i == 3: return (p, q, v)
    if i == 4: return (t, p, v)
    if i == 5: return (v, p, q)

def create_tree(location, trunk_height, trunk_radius, crown_radius, num_branches):
    # Create trunk
    bpy.ops.mesh.primitive_cylinder_add(
        radius=trunk_radius,
        depth=trunk_height,
        location=(location[0], location[1], location[2] + trunk_height/2)
    )
    trunk = bpy.context.active_object
    trunk.name = "TreeTrunk"
    
    # Create tree crown
    bpy.ops.mesh.primitive_ico_sphere_add(
        radius=crown_radius,
        subdivisions=1,
        location=(location[0], location[1], location[2] + trunk_height + crown_radius/2)
    )
    crown = bpy.context.active_object
    crown.name = "TreeCrown"
    
    # Create branches
    branches = []
    for i in range(num_branches):
        angle = random.uniform(0, 2 * math.pi)
        z = random.uniform(trunk_height * 0.3, trunk_height * 0.8)
        x = location[0] + math.cos(angle) * trunk_radius
        y = location[1] + math.sin(angle) * trunk_radius
        
        bpy.ops.mesh.primitive_cone_add(
            radius1=trunk_radius * 0.2,
            radius2=0,
            depth=crown_radius,
            location=(x, y, z)
        )
        branch = bpy.context.active_object
        branch.name = f"TreeBranch_{i}"
        
        # Rotate branch to point outward
        branch.rotation_euler = (math.pi/2, 0, angle)
        branches.append(branch)

    # Generate and apply colors
    trunk_color = (0.3, 0.2, 0.1, 1)  # Brown for trunk
    leaf_hue, leaf_saturation, leaf_value = generate_tree_color()
    leaf_color = hsv_to_rgb(leaf_hue, leaf_saturation, leaf_value) + (1,)  # Add alpha channel
    
    trunk_material = create_material("TrunkMaterial", trunk_color)
    leaf_material = create_material("LeafMaterial", leaf_color)
    
    trunk.data.materials.append(trunk_material)
    crown.data.materials.append(leaf_material)
    
    for branch in branches:
        branch_color = hsv_to_rgb(leaf_hue, leaf_saturation * 0.8, leaf_value * 0.8) + (1,)
        branch_material = create_material(f"BranchMaterial_{branch.name}", branch_color)
        branch.data.materials.append(branch_material)
    
    return trunk, crown, branches

def create_material(name, color):
    material = bpy.data.materials.new(name=name)
    material.use_nodes = True
    material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
    return material

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def add_swaying_animation(obj, strength, speed):
    action = bpy.data.actions.new(name=f"Sway_{obj.name}")
    obj.animation_data_create()
    obj.animation_data.action = action
    
    f_curve_x = action.fcurves.new(data_path="rotation_euler", index=0)
    f_curve_y = action.fcurves.new(data_path="rotation_euler", index=1)
    
    for frame in range(0, 101):
        time = frame / 25.0
        value_x = math.sin(time * speed) * strength
        value_y = math.cos(time * speed * 0.7) * strength * 0.5
        
        f_curve_x.keyframe_points.insert(frame, value_x)
        f_curve_y.keyframe_points.insert(frame, value_y)
    
    for fc in [f_curve_x, f_curve_y]:
        for kf in fc.keyframe_points:
            kf.interpolation = 'LINEAR'

def main():
    clear_scene()
    
    # Create a simple ground plane
    bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "Ground"
    ground_material = create_material("GroundMaterial", (0.2, 0.5, 0.2, 1))
    ground.data.materials.append(ground_material)
    
    # Create trees
    num_trees = 5
    for _ in range(num_trees):
        x = random.uniform(-4, 4)
        y = random.uniform(-4, 4)
        trunk_height = random.uniform(1, 2)
        trunk_radius = random.uniform(0.1, 0.2)
        crown_radius = random.uniform(0.5, 1)
        num_branches = random.randint(3, 7)
        
        trunk, crown, branches = create_tree((x, y, 0), trunk_height, trunk_radius, crown_radius, num_branches)
        
        # Add swaying animation to crown and branches
        add_swaying_animation(crown, 0.05, 1.5)
        for branch in branches:
            strength = random.uniform(0.1, 0.2)
            speed = random.uniform(1, 2)
            add_swaying_animation(branch, strength, speed)
    
    # Set up camera
    bpy.ops.object.camera_add(location=(8, -8, 6), rotation=(math.radians(60), 0, math.radians(45)))
    camera = bpy.context.active_object
    bpy.context.scene.camera = camera
    
    # Set up sun light
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    sun = bpy.context.active_object
    sun.data.energy = 2
    
    # Set up rendering
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 128
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080
    
    # Set up animation
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = 100
    bpy.context.scene.render.fps = 25

    # Export as FBX
    desktop_path = os.path.expanduser("~/Desktop")
    export_path = os.path.join(desktop_path, "colorful_swaying_trees.fbx")
    
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(
        filepath=export_path,
        use_selection=True,
        bake_anim=True,
        bake_anim_use_all_actions=True,
        bake_anim_step=1,
        bake_anim_simplify_factor=1,
        path_mode='COPY',
        embed_textures=True,
        use_mesh_modifiers=True
    )
    
    print(f"Scene exported as FBX to: {export_path}")

if __name__ == "__main__":
    main()
