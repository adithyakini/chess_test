import streamlit as st
import chess
from stockfish import Stockfish
from openai import OpenAI
import chess.polyglot

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)
st.set_page_config(layout="wide")

if "last_explanation" not in st.session_state:
    st.session_state.last_explanation = ""

if "blunders" not in st.session_state:
    st.session_state.blunders = []

if "previous_eval" not in st.session_state:
    st.session_state.previous_eval = None
# --------------------------------------------------
# Evaluation Helper
# --------------------------------------------------
def evaluation_to_cp(evaluation):

    if evaluation["type"] == "cp":
        return evaluation["value"]

    if evaluation["type"] == "mate":

        if evaluation["value"] > 0:
            return 10000

        return -10000

    return 0
# --------------------------------------------------
# STOCKFISH
# --------------------------------------------------

stockfish = Stockfish("/usr/games/stockfish")
stockfish.set_skill_level(10)

#------------------------------------------
#  Chat History for coach interactions
#------------------------------------------

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

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
    opponent_rating = st.slider(
        "Opponent Rating",
        min_value=1200,
        max_value=2850,
        value=1500,
        step=50
    )
    stockfish.set_elo_rating(opponent_rating)
    stockfish.set_fen_position(
        st.session_state.board.fen()
    )

    evaluation = stockfish.get_evaluation()

    best_move = stockfish.get_best_move()
    top_moves = stockfish.get_top_moves(3)

    #------------------------------------------
    # Blunder Detection
    #-------------------------------------------
    stockfish.set_fen_position(
        st.session_state.board.fen()
    )

    before_eval = evaluation_to_cp(
        stockfish.get_evaluation()
    )

    stockfish.set_fen_position(
        st.session_state.board.fen()
    )

    after_eval = evaluation_to_cp(
        stockfish.get_evaluation()
    )
    st.subheader("🎯 Top Candidate Moves")

    for idx, move in enumerate(top_moves, start=1):

        st.write(
            f"{idx}. {move['Move']}"
        )

    st.subheader("📈 Evaluation")
    st.json(evaluation)

    st.subheader("🎯 Best Move")
    st.write(best_move)

    st.subheader("📜 Move History")

    for move in st.session_state.moves:
        st.write(move)

    st.divider()

    st.subheader("🤖 Chess Coach")

    question = st.text_input(
        "Ask Coach",
        placeholder="Why was e4 good?"
    )

    if st.button("Ask Coach") and question:

        with st.spinner("Coach thinking..."):

            move_history = "\n".join(
                st.session_state.moves
            )

            prompt = f"""
You are a professional chess coach.

Current FEN:
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
Keep it concise.
""" 
            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            answer = response.choices[0].message.content

            st.session_state.chat_history.append(
                {
                    "question": question,
                    "answer": answer
                }
            )

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