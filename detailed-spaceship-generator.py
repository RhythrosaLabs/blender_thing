import bpy
import math
import random

def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def create_material(name, color):
    material = bpy.data.materials.new(name=name)
    material.use_nodes = True
    material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
    return material

def create_spaceship_body():
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=1, enter_editmode=False, location=(0, 0, 0))
    body = bpy.context.active_object
    body.name = "SpaceshipBody"
    
    # Flatten the sphere to make it more ship-like
    body.scale = (1, 2, 0.5)
    
    # Add material
    body_material = create_material("BodyMaterial", (0.2, 0.2, 0.8, 1))
    body.data.materials.append(body_material)
    
    return body

def create_cockpit(body):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=0.3, enter_editmode=False, location=(0, 0.8, 0.3))
    cockpit = bpy.context.active_object
    cockpit.name = "Cockpit"
    
    # Add material
    cockpit_material = create_material("CockpitMaterial", (0.8, 0.8, 1, 0.5))
    cockpit.data.materials.append(cockpit_material)
    
    # Parent to body
    cockpit.parent = body
    
    return cockpit

def create_wing(body, side):
    bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, location=(side * 0.8, 0, 0))
    wing = bpy.context.active_object
    wing.name = f"Wing_{side}"
    
    # Shape the wing
    wing.scale = (0.5, 1.5, 0.1)
    
    # Add material
    wing_material = create_material(f"WingMaterial_{side}", (0.5, 0.5, 0.5, 1))
    wing.data.materials.append(wing_material)
    
    # Parent to body
    wing.parent = body
    
    return wing

def create_engine(body, side):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.5, enter_editmode=False, location=(side * 0.5, -1, -0.1))
    engine = bpy.context.active_object
    engine.name = f"Engine_{side}"
    
    # Add material
    engine_material = create_material(f"EngineMaterial_{side}", (0.2, 0.2, 0.2, 1))
    engine.data.materials.append(engine_material)
    
    # Parent to body
    engine.parent = body
    
    return engine

def create_thruster(engine):
    bpy.ops.mesh.primitive_cone_add(radius1=0.15, radius2=0.1, depth=0.2, enter_editmode=False, location=(engine.location.x, engine.location.y - 0.3, engine.location.z))
    thruster = bpy.context.active_object
    thruster.name = f"Thruster_{engine.name}"
    
    # Add material
    thruster_material = create_material(f"ThrusterMaterial_{engine.name}", (0.8, 0.4, 0.1, 1))
    thruster.data.materials.append(thruster_material)
    
    # Parent to engine
    thruster.parent = engine
    
    return thruster

def create_antenna(body):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.3, enter_editmode=False, location=(0, 0, 0.3))
    antenna = bpy.context.active_object
    antenna.name = "Antenna"
    
    # Add material
    antenna_material = create_material("AntennaMaterial", (0.1, 0.1, 0.1, 1))
    antenna.data.materials.append(antenna_material)
    
    # Parent to body
    antenna.parent = body
    
    return antenna

def create_weapon(body, side):
    bpy.ops.mesh.primitive_cube_add(size=0.2, enter_editmode=False, location=(side * 0.5, 0.5, -0.1))
    weapon = bpy.context.active_object
    weapon.name = f"Weapon_{side}"
    
    # Shape the weapon
    weapon.scale = (0.1, 0.3, 0.1)
    
    # Add material
    weapon_material = create_material(f"WeaponMaterial_{side}", (0.3, 0.3, 0.3, 1))
    weapon.data.materials.append(weapon_material)
    
    # Parent to body
    weapon.parent = body
    
    return weapon

def add_engine_glow(engine, thruster):
    # Create light
    bpy.ops.object.light_add(type='POINT', radius=0.1, location=thruster.location)
    light = bpy.context.active_object
    light.name = f"EngineGlow_{engine.name}"
    light.data.color = (1, 0.5, 0.1)
    light.data.energy = 10
    
    # Parent to engine
    light.parent = engine
    
    return light

def add_hover_animation(spaceship, amplitude=0.2, frequency=1):
    spaceship.animation_data_create()
    action = bpy.data.actions.new(name="HoverAnimation")
    spaceship.animation_data.action = action
    
    # Animate Z location
    fcurve = action.fcurves.new(data_path="location", index=2)
    for frame in range(100):
        z_value = amplitude * math.sin(frequency * frame * 2 * math.pi / 100)
        fcurve.keyframe_points.insert(frame, z_value)

def add_weapon_rotation(weapon):
    weapon.animation_data_create()
    action = bpy.data.actions.new(name=f"WeaponRotation_{weapon.name}")
    weapon.animation_data.action = action
    
    # Animate Z rotation
    fcurve = action.fcurves.new(data_path="rotation_euler", index=2)
    for frame in range(100):
        z_value = math.radians(360 * frame / 100)
        fcurve.keyframe_points.insert(frame, z_value)

def add_thruster_flicker(light):
    light.animation_data_create()
    action = bpy.data.actions.new(name=f"ThrusterFlicker_{light.name}")
    light.animation_data.action = action
    
    # Animate light energy
    fcurve = action.fcurves.new(data_path="data.energy")
    for frame in range(100):
        energy = 10 + random.uniform(-2, 2)
        fcurve.keyframe_points.insert(frame, energy)

def setup_camera_and_lighting():
    # Add camera
    bpy.ops.object.camera_add(location=(5, -5, 3), rotation=(math.radians(60), 0, math.radians(45)))
    camera = bpy.context.active_object
    bpy.context.scene.camera = camera

    # Add sun light
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    sun = bpy.context.active_object
    sun.data.energy = 2

def main():
    clear_scene()
    
    # Create spaceship components
    body = create_spaceship_body()
    cockpit = create_cockpit(body)
    
    wing_left = create_wing(body, -1)
    wing_right = create_wing(body, 1)
    
    engine_left = create_engine(body, -1)
    engine_right = create_engine(body, 1)
    
    thruster_left = create_thruster(engine_left)
    thruster_right = create_thruster(engine_right)
    
    antenna = create_antenna(body)
    
    weapon_left = create_weapon(body, -1)
    weapon_right = create_weapon(body, 1)
    
    # Add engine glow
    glow_left = add_engine_glow(engine_left, thruster_left)
    glow_right = add_engine_glow(engine_right, thruster_right)
    
    # Add animations
    add_hover_animation(body)
    add_weapon_rotation(weapon_left)
    add_weapon_rotation(weapon_right)
    add_thruster_flicker(glow_left)
    add_thruster_flicker(glow_right)
    
    setup_camera_and_lighting()
    
    # Set up animation
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = 100
    bpy.context.scene.render.fps = 30
    
    # Set up rendering
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 128
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080

    # Export as FBX
    bpy.ops.export_scene.fbx(filepath="//detailed_spaceship.fbx", use_selection=False)
    print("Detailed spaceship created and exported as FBX.")

if __name__ == "__main__":
    main()
