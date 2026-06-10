import React from "react";
import ReactDOM from "react-dom/client";

import {
  Streamlit,
  withStreamlitConnection
} from "streamlit-component-lib";

import ChessBoard from "./ChessBoard";

const ConnectedBoard =
  withStreamlitConnection(
    ChessBoard
  );

ReactDOM.createRoot(
  document.getElementById("root")
).render(
  <ConnectedBoard />
);