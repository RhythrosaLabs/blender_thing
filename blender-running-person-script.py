import bpy
import math
import os

def delete_all_objects():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def create_simple_human_mesh():
    bpy.ops.mesh.primitive_cube_add(size=0.2, location=(0, 0, 1))
    torso = bpy.context.active_object
    torso.name = "Torso"
    
    bpy.ops.mesh.primitive_cube_add(size=0.2, location=(0, 0, 1.3))
    head = bpy.context.active_object
    head.name = "Head"
    head.scale = (0.8, 0.8, 0.8)
    
    bpy.ops.mesh.primitive_cube_add(size=0.1, location=(0.15, 0, 0.9))
    arm_r = bpy.context.active_object
    arm_r.name = "Arm_R"
    arm_r.scale = (0.4, 0.6, 1.5)
    
    bpy.ops.mesh.primitive_cube_add(size=0.1, location=(-0.15, 0, 0.9))
    arm_l = bpy.context.active_object
    arm_l.name = "Arm_L"
    arm_l.scale = (0.4, 0.6, 1.5)
    
    bpy.ops.mesh.primitive_cube_add(size=0.1, location=(0.06, 0, 0.5))
    leg_r = bpy.context.active_object
    leg_r.name = "Leg_R"
    leg_r.scale = (0.6, 0.6, 2)
    
    bpy.ops.mesh.primitive_cube_add(size=0.1, location=(-0.06, 0, 0.5))
    leg_l = bpy.context.active_object
    leg_l.name = "Leg_L"
    leg_l.scale = (0.6, 0.6, 2)
    
    body_parts = [torso, head, arm_r, arm_l, leg_r, leg_l]
    
    for part in body_parts[1:]:
        part.select_set(True)
        torso.select_set(True)
        bpy.context.view_layer.objects.active = torso
    
    bpy.ops.object.join()
    
    return torso

def create_armature():
    bpy.ops.object.armature_add(location=(0, 0, 0))
    armature = bpy.context.active_object
    armature.name = "Human_Armature"
    
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Create bones
    bones = armature.data.edit_bones
    
    spine = bones["Bone"]
    spine.name = "Spine"
    spine.head = (0, 0, 0.9)
    spine.tail = (0, 0, 1.1)
    
    head = bones.new("Head")
    head.head = spine.tail
    head.tail = (0, 0, 1.3)
    head.parent = spine
    
    upper_arm_r = bones.new("Upper_Arm_R")
    upper_arm_r.head = (0.15, 0, 1.1)
    upper_arm_r.tail = (0.15, 0, 0.9)
    upper_arm_r.parent = spine
    
    upper_arm_l = bones.new("Upper_Arm_L")
    upper_arm_l.head = (-0.15, 0, 1.1)
    upper_arm_l.tail = (-0.15, 0, 0.9)
    upper_arm_l.parent = spine
    
    thigh_r = bones.new("Thigh_R")
    thigh_r.head = (0.06, 0, 0.9)
    thigh_r.tail = (0.06, 0, 0.5)
    thigh_r.parent = spine
    
    thigh_l = bones.new("Thigh_L")
    thigh_l.head = (-0.06, 0, 0.9)
    thigh_l.tail = (-0.06, 0, 0.5)
    thigh_l.parent = spine
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return armature

def parent_mesh_to_armature(mesh, armature):
    mesh.parent = armature
    mesh.modifiers.new(name="Armature", type='ARMATURE')
    mesh.modifiers["Armature"].object = armature

def create_run_animation(armature, num_frames=40):
    bpy.context.scene.frame_end = num_frames
    
    bpy.ops.object.mode_set(mode='POSE')
    
    pose_bones = armature.pose.bones
    
    for frame in range(num_frames):
        bpy.context.scene.frame_set(frame)
        
        t = frame / num_frames
        
        # Spine and head movement
        pose_bones["Spine"].rotation_quaternion = (1, 0.1 * math.sin(t * 2 * math.pi), 0, 0)
        pose_bones["Head"].rotation_quaternion = (1, -0.05 * math.sin(t * 2 * math.pi), 0, 0)
        
        # Arm movement
        pose_bones["Upper_Arm_R"].rotation_quaternion = (1, 0, 0, 0.5 * math.cos(t * 2 * math.pi))
        pose_bones["Upper_Arm_L"].rotation_quaternion = (1, 0, 0, 0.5 * math.cos(t * 2 * math.pi + math.pi))
        
        # Leg movement
        pose_bones["Thigh_R"].rotation_quaternion = (1, 0.7 * math.cos(t * 2 * math.pi), 0, 0)
        pose_bones["Thigh_L"].rotation_quaternion = (1, 0.7 * math.cos(t * 2 * math.pi + math.pi), 0, 0)
        
        # Insert keyframes
        for bone in pose_bones:
            bone.keyframe_insert(data_path="rotation_quaternion")
    
    bpy.ops.object.mode_set(mode='OBJECT')

# Clear existing objects
delete_all_objects()

# Set up the scene
bpy.context.scene.render.fps = 24

# Create the human mesh
human_mesh = create_simple_human_mesh()

# Create the armature
armature = create_armature()

# Parent the mesh to the armature
parent_mesh_to_armature(human_mesh, armature)

# Create the run animation
create_run_animation(armature)

# Get the path to the desktop
desktop_path = os.path.expanduser("~/Desktop")

# Set the export path
export_path = os.path.join(desktop_path, "running_person.fbx")

# Select the armature and mesh
bpy.ops.object.select_all(action='DESELECT')
armature.select_set(True)
human_mesh.select_set(True)
bpy.context.view_layer.objects.active = armature

# Export as FBX
bpy.ops.export_scene.fbx(filepath=export_path, use_selection=True, bake_anim=True)

print(f"Animated running person exported as FBX to: {export_path}")
