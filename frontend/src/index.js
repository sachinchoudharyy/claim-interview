import React, { useContext } from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./styles/global.css";
import { BrowserRouter } from "react-router-dom";

import { AuthProvider } from "./context/AuthContext";

import { LoadingProvider, LoadingContext } from "./context/LoadingContext";
import Loader from "./components/Loader";

const root = ReactDOM.createRoot(document.getElementById("root"));

function AppWrapper() {
  const { loading } = useContext(LoadingContext);

  return (
    <>
      {loading && <Loader />}
      <App />
    </>
  );
}

root.render(
  <BrowserRouter>
    <AuthProvider>
      <LoadingProvider>
        <AppWrapper />
      </LoadingProvider>
    </AuthProvider>
  </BrowserRouter>
);