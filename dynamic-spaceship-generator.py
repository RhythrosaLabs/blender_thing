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
    bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=3, enter_editmode=False, location=(0, 0, 0))
    body = bpy.context.active_object
    body.name = "SpaceshipBody"
    
    # Taper the body
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_mode(type='VERT')
    bpy.ops.object.mode_set(mode='OBJECT')
    for v in body.data.vertices:
        if v.co.y > 1:
            v.select = True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.transform.resize(value=(0.5, 0.5, 0.5))
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Add material
    body_material = create_material("BodyMaterial", (0.1, 0.1, 0.3, 1))
    body.data.materials.append(body_material)
    
    return body

def create_wings(body):
    bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, location=(0.7, 0, 0))
    wing_r = bpy.context.active_object
    wing_r.name = "Wing_R"
    wing_r.scale = (1, 0.1, 0.5)
    wing_r.parent = body
    
    bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, location=(-0.7, 0, 0))
    wing_l = bpy.context.active_object
    wing_l.name = "Wing_L"
    wing_l.scale = (1, 0.1, 0.5)
    wing_l.parent = body
    
    wing_material = create_material("WingMaterial", (0.2, 0.2, 0.4, 1))
    wing_r.data.materials.append(wing_material)
    wing_l.data.materials.append(wing_material)
    
    return wing_r, wing_l

def create_engines(body):
    engines = []
    for i in range(3):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.5, enter_editmode=False, location=(0.3*(i-1), -1.5, -0.1))
        engine = bpy.context.active_object
        engine.name = f"Engine_{i}"
        engine.parent = body
        
        engine_material = create_material(f"EngineMaterial_{i}", (0.1, 0.1, 0.1, 1))
        engine.data.materials.append(engine_material)
        
        engines.append(engine)
    
    return engines

def create_cockpit(body):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=0.3, enter_editmode=False, location=(0, 1.2, 0.2))
    cockpit = bpy.context.active_object
    cockpit.name = "Cockpit"
    cockpit.scale = (0.5, 0.7, 0.4)
    
    cockpit_material = create_material("CockpitMaterial", (0.8, 0.9, 1, 0.3))
    cockpit.data.materials.append(cockpit_material)
    
    cockpit.parent = body
    
    return cockpit

def add_engine_glow(engine):
    bpy.ops.object.light_add(type='POINT', radius=0.1, location=engine.location)
    light = bpy.context.active_object
    light.name = f"EngineGlow_{engine.name}"
    light.data.color = (0.2, 0.5, 1)
    light.data.energy = 10
    light.parent = engine
    return light

def add_complex_flight_path(spaceship):
    spaceship.animation_data_create()
    action = bpy.data.actions.new(name="ComplexFlightPath")
    spaceship.animation_data.action = action
    
    # Create flight path
    frames = 300
    for i in range(4):  # x, y, z, rotation
        fcurve = action.fcurves.new(data_path="location", index=i) if i < 3 else action.fcurves.new(data_path="rotation_euler", index=0)
        for frame in range(frames):
            t = frame / frames
            if i == 0:  # X location
                value = 10 * math.sin(t * 2 * math.pi)
            elif i == 1:  # Y location
                value = 20 * t - 10
            elif i == 2:  # Z location
                value = 5 * math.sin(t * 4 * math.pi)
            else:  # Rotation (barrel roll)
                value = 4 * math.pi * t
            fcurve.keyframe_points.insert(frame, value)

def add_engine_pulsing(lights):
    for light in lights:
        light.animation_data_create()
        action = bpy.data.actions.new(name=f"EnginePulse_{light.name}")
        light.animation_data.action = action
        
        fcurve = action.fcurves.new(data_path="data.energy")
        frames = 60
        for frame in range(frames):
            t = frame / frames
            energy = 10 + 5 * math.sin(t * 2 * math.pi)
            fcurve.keyframe_points.insert(frame, energy)

def setup_camera_and_lighting():
    bpy.ops.object.camera_add(location=(0, -20, 5), rotation=(math.radians(80), 0, 0))
    camera = bpy.context.active_object
    bpy.context.scene.camera = camera

    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    sun = bpy.context.active_object
    sun.data.energy = 3

def main():
    clear_scene()
    
    body = create_spaceship_body()
    wing_r, wing_l = create_wings(body)
    engines = create_engines(body)
    cockpit = create_cockpit(body)
    
    engine_lights = [add_engine_glow(engine) for engine in engines]
    
    add_complex_flight_path(body)
    add_engine_pulsing(engine_lights)
    
    setup_camera_and_lighting()
    
    # Set up animation
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = 300
    bpy.context.scene.render.fps = 30
    
    # Set up rendering
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 128
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080

    # Export as FBX
    bpy.ops.export_scene.fbx(filepath="//dynamic_spaceship.fbx", use_selection=False)
    print("Dynamic spaceship created and exported as FBX.")

if __name__ == "__main__":
    main()
