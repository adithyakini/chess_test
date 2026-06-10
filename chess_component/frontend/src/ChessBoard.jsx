import { useState } from "react";
import { Chessboard } from "react-chessboard";
import { Chess } from "chess.js";

import {
  Streamlit
} from "streamlit-component-lib";

function ChessBoard(props) {

  const [game, setGame] =
    useState(
      () => new Chess()
    );

  const chessboardOptions = {

    position: game.fen(),

    onPieceDrop: (
      moveData
    ) => {

      const gameCopy =
        new Chess(
          game.fen()
        );

      const move =
        gameCopy.move({
          from:
            moveData.sourceSquare,
          to:
            moveData.targetSquare,
          promotion: "q"
        });

      if (!move) {
        return false;
      }

      setGame(gameCopy);

      Streamlit.setComponentValue({
        move:
          moveData.sourceSquare +
          moveData.targetSquare,
        fen:
          gameCopy.fen()
      });

      return true;
    }
  };

  return (
    <div>
      <h2>React Component Loaded</h2>

      <Chessboard
        options={chessboardOptions}
      />
    </div>
  );
}

export default ChessBoard;