import React from "react";
import { createRoot } from "react-dom/client";
import { widget as ReactWidget } from "adhocracy4";
import ArBase from "./Prototype";

function init() {
  ReactWidget.initialise("aplus", "arpas", function (el) {
    const root = createRoot(el);
    root.render(
      <React.StrictMode>
        <ArBase {...el.dataset} />
      </React.StrictMode>
    );
  });
}

document.addEventListener("DOMContentLoaded", init, false);
