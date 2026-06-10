import streamlit as st
from stockfish import Stockfish

st.title("Stockfish Debug")

try:

    stockfish = Stockfish(
        path="/usr/games/stockfish"
    )

    st.write(dir(stockfish))

except Exception as e:

    st.error(str(e))