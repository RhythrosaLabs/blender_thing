import bpy
import math
import random
import os

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def create_ground(size):
    bpy.ops.mesh.primitive_plane_add(size=size, enter_editmode=False, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "Ground"
    material = bpy.data.materials.new(name="GroundMaterial")
    material.use_nodes = True
    material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.1, 0.2, 0.05, 1)  # Dark green
    ground.data.materials.append(material)
    return ground

def create_grass_patch(num_blades, area_size):
    bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=True)
    bpy.ops.mesh.subdivide(number_cuts=int(math.sqrt(num_blades))-1)
    bpy.ops.object.mode_set(mode='OBJECT')
    grass_patch = bpy.context.active_object
    grass_patch.name = "GrassPatch"

    for v in grass_patch.data.vertices:
        v.co.x += random.uniform(-0.5, 0.5) * 0.1
        v.co.y += random.uniform(-0.5, 0.5) * 0.1
        v.co.z = random.uniform(0.1, 0.3)

    material = bpy.data.materials.new(name="GrassMaterial")
    material.use_nodes = True
    material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.1, 0.5, 0.1, 1)  # Green
    grass_patch.data.materials.append(material)

    grass_patch.scale = (area_size, area_size, 1)
    return grass_patch

def create_simple_tree(location, scale):
    bpy.ops.mesh.primitive_cone_add(radius1=0.5, radius2=0, depth=2, location=(location[0], location[1], location[2]+1))
    tree = bpy.context.active_object
    tree.name = f"Tree_{location[0]}_{location[1]}"
    tree.scale = (scale, scale, scale)

    material = bpy.data.materials.new(name=f"TreeMaterial_{tree.name}")
    material.use_nodes = True
    material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.1, 0.3 + random.uniform(0, 0.2), 0.1, 1)  # Varied green
    tree.data.materials.append(material)

    return tree

def create_simple_human():
    bpy.ops.mesh.primitive_cube_add(size=0.2, location=(0, 0, 1))
    torso = bpy.context.active_object
    torso.name = "Human"
    torso.scale = (1, 0.5, 1.5)

    bpy.ops.mesh.primitive_cube_add(size=0.2, location=(0, 0, 1.4))
    head = bpy.context.active_object
    head.name = "Head"
    head.scale = (0.8, 0.8, 0.8)
    head.parent = torso

    material = bpy.data.materials.new(name="HumanMaterial")
    material.use_nodes = True
    material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.8, 0.6, 0.5, 1)  # Skin color
    torso.data.materials.append(material)
    head.data.materials.append(material)

    return torso

def create_human_armature():
    bpy.ops.object.armature_add(location=(0, 0, 0))
    armature = bpy.context.active_object
    armature.name = "Human_Armature"

    bpy.ops.object.mode_set(mode='EDIT')
    bones = armature.data.edit_bones
    bones["Bone"].name = "Spine"
    bones["Spine"].head = (0, 0, 0.9)
    bones["Spine"].tail = (0, 0, 1.5)
    bpy.ops.object.mode_set(mode='OBJECT')

    return armature

def parent_to_armature(obj, armature):
    obj.parent = armature
    obj.modifiers.new(name="Armature", type='ARMATURE')
    obj.modifiers["Armature"].object = armature

def add_walk_animation(armature, distance=5):
    armature.animation_data_create()
    action = bpy.data.actions.new(name="WalkAction")
    armature.animation_data.action = action

    frames = 50
    bpy.context.scene.frame_end = frames

    for frame in range(frames + 1):
        bpy.context.scene.frame_set(frame)
        t = frame / frames
        armature.location = (t * distance, 0, math.sin(t * 2 * math.pi) * 0.1)
        armature.keyframe_insert(data_path="location", frame=frame)

def main():
    clear_scene()

    ground_size = 10
    ground = create_ground(ground_size)

    grass_patch = create_grass_patch(500, ground_size)

    num_trees = 5
    for _ in range(num_trees):
        x = random.uniform(-ground_size/2, ground_size/2)
        y = random.uniform(-ground_size/2, ground_size/2)
        scale = random.uniform(0.5, 1.5)
        create_simple_tree((x, y, 0), scale)

    human = create_simple_human()
    armature = create_human_armature()
    parent_to_armature(human, armature)

    add_walk_animation(armature)

    bpy.ops.object.camera_add(location=(5, -5, 3), rotation=(math.radians(60), 0, math.radians(45)))
    camera = bpy.context.active_object
    bpy.context.scene.camera = camera

    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    sun = bpy.context.active_object
    sun.data.energy = 2

    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 128
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080

    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = 50
    bpy.context.scene.render.fps = 24

    desktop_path = os.path.expanduser("~/Desktop")
    export_path = os.path.join(desktop_path, "optimized_nature_scene.fbx")

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

    print(f"Optimized nature scene exported as FBX to: {export_path}")

if __name__ == "__main__":
    main()
