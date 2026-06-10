import streamlit as st
import chess
from stockfish import Stockfish

st.set_page_config(layout="wide")

# --------------------------------------------------
# STOCKFISH
# --------------------------------------------------

stockfish = Stockfish("/usr/games/stockfish")
stockfish.set_skill_level(10)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "board" not in st.session_state:
    st.session_state.board = chess.Board()

if "moves" not in st.session_state:
    st.session_state.moves = []

# --------------------------------------------------
# LAYOUT
# --------------------------------------------------

left, right = st.columns([2, 1])

with left:

    st.title("♟️ Chess Coach")

    st.subheader("Current Position")

    st.code(st.session_state.board.fen())

    move = st.text_input(
        "Your Move (UCI)",
        placeholder="e2e4"
    )

    if st.button("Play Move"):

        try:

            user_move = chess.Move.from_uci(move)

            if user_move in st.session_state.board.legal_moves:

                st.session_state.board.push(user_move)

                st.session_state.moves.append(
                    f"You: {move}"
                )

                # AI TURN
                stockfish.set_fen_position(
                    st.session_state.board.fen()
                )

                ai_move = stockfish.get_best_move()

                if ai_move:

                    st.session_state.board.push_uci(
                        ai_move
                    )

                    st.session_state.moves.append(
                        f"AI: {ai_move}"
                    )

                st.rerun()

            else:

                st.error("Illegal move")

        except Exception as e:

            st.error(str(e))

with right:

    st.subheader("Move History")

    for move in st.session_state.moves:
        st.write(move)

    stockfish.set_fen_position(
        st.session_state.board.fen()
    )

    evaluation = stockfish.get_evaluation()

    best_move = stockfish.get_best_move()

    st.subheader("Evaluation")

    st.json(evaluation)

    st.subheader("Best Move")

    st.write(best_move)