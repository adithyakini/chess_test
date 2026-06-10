import streamlit as st
from stockfish import Stockfish

st.title("♟️ Stockfish Test")

try:

    stockfish = Stockfish(
        path="/usr/games/stockfish"
    )

    stockfish.set_position(["e2e4"])

    best_move = stockfish.get_best_move()

    st.success(
        f"Stockfish says: {best_move}"
    )

except Exception as e:

    st.error(str(e))