import streamlit as st
import chess

st.set_page_config(layout="wide")

st.title("♟️ Chess Coach")

if "board" not in st.session_state:
    st.session_state.board = chess.Board()

st.write("Current Position")

st.code(st.session_state.board.fen())

move = st.text_input(
    "Enter move (UCI)",
    placeholder="e2e4"
)

if st.button("Play Move"):

    try:

        chess_move = chess.Move.from_uci(
            move
        )

        if chess_move in st.session_state.board.legal_moves:

            st.session_state.board.push(
                chess_move
            )

            st.success("Move played")

        else:

            st.error("Illegal move")

    except:

        st.error("Invalid move")