import streamlit as st
import chess
from stockfish import Stockfish

st.title("♟️ Stockfish Test")

try:
    stockfish = Stockfish(
        path="./stockfish/stockfish.exe"
    )

    stockfish.set_position(["e2e4"])

    best_move = stockfish.get_best_move()

    st.success(f"Stockfish says: {best_move}")

except Exception as e:
    st.error(str(e))