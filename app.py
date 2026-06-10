import streamlit as st
import os

st.title("Find Stockfish")

for root, dirs, files in os.walk("/usr"):
    for file in files:
        if "stockfish" in file.lower():
            st.write(
                os.path.join(root, file)
            )