import streamlit as st
from stockfish import Stockfish

st.title("♟️ Stockfish Cloud Test")

try:

    stockfish = Stockfish(
        path="/usr/games/stockfish"
    )

    stockfish.set_fen_position(
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
    )

    best_move = stockfish.get_best_move()

    evaluation = stockfish.get_evaluation()

    st.success(f"Best move: {best_move}")

    st.write("Evaluation:")

    st.json(evaluation)

except Exception as e:

    st.error(str(e))