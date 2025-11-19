import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "bootstrap/dist/css/bootstrap.min.css";
import "./index.css";
import { AppStoreProvider } from "./AppStoreProvider";
import { registerSW } from "virtual:pwa-register";

const container = document.getElementById("root")!;
const root = createRoot(container);
root.render(
  <React.StrictMode>
    <AppStoreProvider>
      <BrowserRouter basename="/vasoactive_drug_speed_estimatior_frontend">
        <App />
      </BrowserRouter>
    </AppStoreProvider>
  </React.StrictMode>
);

if ("serviceWorker" in navigator) {
  registerSW();
}
