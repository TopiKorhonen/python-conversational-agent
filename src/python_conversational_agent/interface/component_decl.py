import os
import streamlit.components.v1 as components

# Declare the component in an imported module so Streamlit can inspect it correctly
PARENT_DIR = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.join(PARENT_DIR, "pages", "frontend")

threejs_viewer_component = components.declare_component(
    "threejs_viewer",
    path=BUILD_DIR
)

threejs_mascot_component = components.declare_component(
    "threejs_mascot",
    path=os.path.join(PARENT_DIR, "mascot_frontend")
)
