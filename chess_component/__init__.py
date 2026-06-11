import os
import streamlit as st
import streamlit.components.v1 as components

parent_dir = os.path.dirname(os.path.abspath(__file__))

build_dir = os.path.join(
    parent_dir,
    "frontend",
    "dist"
)

print("BUILD DIR:", build_dir)
print("EXISTS:", os.path.exists(build_dir))
print("INDEX:", os.path.exists(os.path.join(build_dir, "index.html")))

_component_func = components.declare_component(
    "chessboard",
    path=build_dir
)

def st_chessboard(fen="start"):
    return _component_func(
        fen=fen,
        default=None
    )