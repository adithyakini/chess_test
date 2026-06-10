import streamlit as st
import chess
from stockfish import Stockfish
from openai import OpenAI

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Chess Coach",
    layout="wide"
)

# --------------------------------------------------
# OPENAI
# --------------------------------------------------

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def get_stockfish():
    sf = Stockfish("/usr/games/stockfish")
    return sf

def evaluation_to_text(evaluation):

    if evaluation["type"] == "cp":
        return f"{evaluation['value']/100:+.2f}"

    if evaluation["type"] == "mate":
        return f"Mate in {evaluation['value']}"

    return "Unknown"

def evaluation_to_cp(evaluation):

    if evaluation["type"] == "cp":
        return evaluation["value"]

    if evaluation["type"] == "mate":

        if evaluation["value"] > 0:
            return 10000

        return -10000

    return 0

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "board" not in st.session_state:
    st.session_state.board = chess.Board()

if "moves" not in st.session_state:
    st.session_state.moves = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "opponent_rating" not in st.session_state:
    st.session_state.opponent_rating = 1500

if "mistakes" not in st.session_state:
    st.session_state.mistakes = []

if "previous_fen" not in st.session_state:
    st.session_state.previous_fen = None

if "previous_eval" not in st.session_state:
    st.session_state.previous_eval = None

if "auto_coach_messages" not in st.session_state:
    st.session_state.auto_coach_messages = []
# --------------------------------------------------
# LAYOUT
# --------------------------------------------------

left, right = st.columns([2, 1])

# ==================================================
# LEFT PANEL
# ==================================================

with left:

    st.title("♟️ Chess Coach")

    if st.button("♻️ New Game"):

        st.session_state.board = chess.Board()
        st.session_state.moves = []
        st.session_state.chat_history = []

        st.rerun()

    st.subheader("Current Position")

    st.code(
        st.session_state.board.fen()
    )

    move = st.text_input(
        "Your Move (UCI)",
        placeholder="e2e4"
    )

    if st.button("Play Move"):

        try:

            user_move = chess.Move.from_uci(move)

            if user_move in st.session_state.board.legal_moves:
                stockfish = get_stockfish()

                stockfish.set_elo_rating(
                    st.session_state.opponent_rating
                )

                stockfish.set_fen_position(
                    st.session_state.board.fen()
                )

                before_eval = stockfish.get_evaluation()

                st.session_state.previous_fen = (
                    st.session_state.board.fen()
                )

                st.session_state.previous_eval = (
                    before_eval
                )
                st.session_state.board.push(
                    user_move
                )

                st.session_state.moves.append(
                    f"You: {move}"
                )

                stockfish = get_stockfish()

                stockfish.set_elo_rating(
                    st.session_state.opponent_rating
                )

                stockfish.set_fen_position(
                    st.session_state.board.fen()
                )
                stockfish.set_fen_position(
                    st.session_state.board.fen()
                )

                after_eval = stockfish.get_evaluation()

                loss = (
                    evaluation_to_cp(after_eval)
                    -
                    evaluation_to_cp(before_eval)
                )
                            
                mistake_type = None

                if loss < -500:
                    mistake_type = "🚨 Blunder"

                elif loss < -250:
                    mistake_type = "⚠️ Mistake"
                    
                elif loss < -100:
                    mistake_type = "ℹ️ Inaccuracy"
                if mistake_type:

                    st.session_state.mistakes.append(
                        {
                            "move": move,
                            "loss": loss,
                            "type": mistake_type
                        }
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

                st.error(
                    "Illegal move"
                )

        except Exception as e:

            st.error(str(e))

# ==================================================
# RIGHT PANEL
# ==================================================

with right:

    st.subheader("🎚 Opponent Rating")

    opponent_rating = st.slider(
        "Rating",
        min_value=1350,
        max_value=2850,
        value=st.session_state.opponent_rating,
        step=50,
        label_visibility="collapsed"
    )

    st.session_state.opponent_rating = (
        opponent_rating
    )

    stockfish = get_stockfish()

    stockfish.set_elo_rating(
        opponent_rating
    )

    stockfish.set_fen_position(
        st.session_state.board.fen()
    )

    evaluation = stockfish.get_evaluation()

    try:

        top_moves = stockfish.get_top_moves(3)

    except Exception:

        top_moves = []

    st.subheader(
        "🎯 Candidate Moves"
    )

    if top_moves:

        for idx, move_data in enumerate(
            top_moves,
            start=1
        ):

            st.write(
                f"{idx}. {move_data['Move']}"
            )

    else:

        st.caption(
            "No candidate moves available"
        )

    st.subheader("📈 Evaluation")

    st.metric(
        "Position",
        evaluation_to_text(
            evaluation
        )
    )

    st.subheader("📜 Move History")
    st.subheader("⚠️ Mistakes")

    if not st.session_state.mistakes:

        st.caption(
            "No mistakes detected."
        )

    else:

        for m in reversed(
            st.session_state.mistakes
        ):

            st.write(
                f"{m['type']} "
                f"{m['move']} "
                f"({m['loss']} cp)"
            )
            
    if not st.session_state.moves:

        st.caption(
            "No moves yet"
        )

    else:

        for move in st.session_state.moves:

            st.write(move)

    st.divider()

    st.subheader("🤖 Chess Coach")

    question = st.text_input(
        "Ask Coach",
        placeholder="Why was e4 good?"
    )

    if st.button("Ask Coach") and question:

        with st.spinner(
            "Coach thinking..."
        ):

            move_history = "\n".join(
                st.session_state.moves
            )

            prompt = f"""
You are a professional FIDE chess coach.

Current Position:
{st.session_state.board.fen()}

Move History:
{move_history}

Engine Evaluation:
{evaluation}

Student Question:
{question}

Give a practical chess explanation.

Focus on:
- plans
- tactics
- positional ideas

Keep answer under 200 words.
"""

            response = (
                client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
            )

            answer = (
                response
                .choices[0]
                .message
                .content
            )

            st.session_state.chat_history.append(
                {
                    "question": question,
                    "answer": answer
                }
            )

            st.rerun()

    for chat in reversed(
        st.session_state.chat_history
    ):

        st.markdown(
            f"**You:** {chat['question']}"
        )

        st.markdown(
            f"**Coach:** {chat['answer']}"
        )

        st.divider()