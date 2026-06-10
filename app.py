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
# STOCKFISH
# --------------------------------------------------

@st.cache_resource
def get_stockfish():
    return Stockfish("/usr/games/stockfish")

stockfish = get_stockfish()

# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def evaluation_to_text(evaluation):

    if evaluation["type"] == "cp":
        return f"{evaluation['value']/100:+.2f}"

    if evaluation["type"] == "mate":
        return f"Mate in {evaluation['value']}"

    return "Unknown"

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "board" not in st.session_state:
    st.session_state.board = chess.Board()

if "moves" not in st.session_state:
    st.session_state.moves = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --------------------------------------------------
# LAYOUT
# --------------------------------------------------

left, right = st.columns([2, 1])

# ==================================================
# LEFT PANEL
# ==================================================

with left:

    st.title("♟️ Chess Coach")

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

                st.session_state.board.push(
                    user_move
                )

                st.session_state.moves.append(
                    f"You: {move}"
                )

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
        value=1500,
        step=50,
        label_visibility="collapsed"
    )

    try:

        stockfish.set_elo_rating(
            opponent_rating
        )

    except:

        stockfish.set_skill_level(10)

    stockfish.set_fen_position(
        st.session_state.board.fen()
    )

    evaluation = stockfish.get_evaluation()

    top_moves = stockfish.get_top_moves(3)

    st.subheader(
        "🎯 Top Candidate Moves"
    )

    if top_moves:

        for idx, move_data in enumerate(
            top_moves,
            start=1
        ):

            st.write(
                f"{idx}. {move_data['Move']}"
            )

    st.subheader("📈 Evaluation")

    st.metric(
        "Position",
        evaluation_to_text(
            evaluation
        )
    )

    st.subheader("📜 Move History")

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
You are a FIDE chess coach.

Current Position:
{st.session_state.board.fen()}

Move History:
{move_history}

Engine Evaluation:
{evaluation}

Best Move:
{best_move}

Student Question:
{question}

Give a practical chess explanation.

Focus on:
- Plans
- Tactical ideas
- Strategic concepts

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