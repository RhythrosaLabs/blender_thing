import streamlit as st
import openai
import subprocess
import os
import zipfile
import tempfile

# Set up your OpenAI API key
openai.api_key = "your-api-key-here"

def generate_blender_script(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates Blender Python scripts."},
            {"role": "user", "content": f"Generate a complex Blender Python script for creating a {prompt}. Include animations and export as FBX."}
        ]
    )
    return response.choices[0].message.content

def run_blender_script(script):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_script:
        temp_script.write(script)
        temp_script_path = temp_script.name

    with tempfile.TemporaryDirectory() as temp_dir:
        output_fbx = os.path.join(temp_dir, "output.fbx")
        blender_command = [
            "blender",
            "--background",
            "--python", temp_script_path,
            "--",
            output_fbx
        ]
        subprocess.run(blender_command, check=True)

        zip_path = os.path.join(temp_dir, "output.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(output_fbx, arcname="output.fbx")

        with open(zip_path, "rb") as f:
            return f.read()

    os.unlink(temp_script_path)

st.title("Blender Script Generator")

user_input = st.text_input("Enter a description (e.g., 'spaceship'):")

if st.button("Generate and Download"):
    if user_input:
        with st.spinner("Generating Blender script..."):
            blender_script = generate_blender_script(user_input)

        st.text_area("Generated Blender Script:", value=blender_script, height=300)

        with st.spinner("Running Blender script and generating FBX..."):
            try:
                zip_data = run_blender_script(blender_script)
                st.download_button(
                    label="Download FBX (Zipped)",
                    data=zip_data,
                    file_name="blender_output.zip",
                    mime="application/zip"
                )
            except subprocess.CalledProcessError:
                st.error("Error running Blender script. Please check the script for errors.")
    else:
        st.warning("Please enter a description.")
