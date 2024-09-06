import bpy
import random
import math
import os

def create_ground(size):
    bpy.ops.mesh.primitive_plane_add(size=size, enter_editmode=False, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "Ground"
    material = bpy.data.materials.new(name="GroundMaterial")
    material.use_nodes = True
    material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.1, 0.2, 0.05, 1)  # Dark green
    ground.data.materials.append(material)
    return ground

def create_grass_blade(location, height):
    bpy.ops.mesh.primitive_plane_add(size=0.1, enter_editmode=False, location=location)
    grass = bpy.context.active_object
    grass.name = f"GrassBlade_{location[0]}_{location[1]}"
    
    # Extrude the plane to create a blade shape
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, 0, height)})
    bpy.ops.transform.resize(value=(0.1, 1, 1))
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Rotate randomly
    grass.rotation_euler = (0, 0, random.uniform(0, 2 * math.pi))
    
    # Add material
    material = bpy.data.materials.new(name=f"GrassMaterial_{grass.name}")
    material.use_nodes = True
    material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.1, 0.5 + random.uniform(0, 0.5), 0.1, 1)  # Varied green
    grass.data.materials.append(material)
    
    return grass

def create_rock(location, size):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=size, enter_editmode=False, location=location)
    rock = bpy.context.active_object
    rock.name = f"Rock_{location[0]}_{location[1]}"
    
    # Add some randomness to the shape
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.random_vertex_group(seed=random.randint(0, 1000), count=10)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Add material
    material = bpy.data.materials.new(name=f"RockMaterial_{rock.name}")
    material.use_nodes = True
    material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.2 + random.uniform(0, 0.1), 0.2 + random.uniform(0, 0.1), 0.2 + random.uniform(0, 0.1), 1)  # Varied dark gray
    rock.data.materials.append(material)
    
    return rock

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
    # Clear existing scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Create ground
    ground_size = 10
    ground = create_ground(ground_size)
    
    # Create grass
    num_grass_blades = 500
    for _ in range(num_grass_blades):
        x = random.uniform(-ground_size/2, ground_size/2)
        y = random.uniform(-ground_size/2, ground_size/2)
        height = random.uniform(0.1, 0.3)
        grass_blade = create_grass_blade((x, y, 0), height)
        add_swaying_animation(grass_blade, random.uniform(0.1, 0.3), random.uniform(1, 2))
    
    # Create rocks
    num_rocks = 20
    for _ in range(num_rocks):
        x = random.uniform(-ground_size/2, ground_size/2)
        y = random.uniform(-ground_size/2, ground_size/2)
        size = random.uniform(0.2, 0.6)
        create_rock((x, y, size/2), size)
    
    # Set up camera
    bpy.ops.object.camera_add(location=(5, -5, 3), rotation=(math.radians(60), 0, math.radians(45)))
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
    export_path = os.path.join(desktop_path, "swaying_grass_and_rocks.fbx")
    
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
