import streamlit as st
from stockfish import Stockfish

st.title("Stockfish Test")

try:
    stockfish = Stockfish("/usr/games/stockfish")

    stockfish.set_position(["e2e4"])

    st.success(
        f"Best move: {stockfish.get_best_move()}"
    )

except Exception as e:
    st.error(str(e))