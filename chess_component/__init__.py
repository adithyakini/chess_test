import os
import streamlit.components.v1 as components

parent_dir = os.path.dirname(
    os.path.abspath(__file__)
)

build_dir = os.path.join(
    parent_dir,
    "frontend",
    "dist"
)

_component_func = (
    components.declare_component(
        "chessboard",
        path=build_dir
    )
)

def st_chessboard(fen="start"):

    return _component_func(
        fen=fen,
        default=None
    )