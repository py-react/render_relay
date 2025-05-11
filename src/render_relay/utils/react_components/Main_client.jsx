import React from "react";
import Router from "./BrowserRouterWrapper";
import { hydrateRoot } from "react-dom/client";
import App from "./app";
function getServerProps(props) {
  try {
    if (window !== undefined) {
      const data = JSON.parse(JSON.stringify(window.fastApi_react_app_props));
      return { ...data, ...props };
    }
  } catch (error) {
    // pass
  }
  return props;
}

function handleHydrationError(error, errorInfo) {
  console.error("Hydration error:", { error, errorInfo });

  // Create the error overlay elements
  const overlay = document.createElement("div");
  overlay.id = "error-overlay";

  const messageBox = document.createElement("div");
  messageBox.id = "error-message";

  const closeButton = document.createElement("button");
  closeButton.id = "close-overlay";
  closeButton.textContent = "Close";

  const title = document.createElement("h2");
  title.textContent = error.message;

  const details = document.createElement("pre");
  details.id = "error-details";
  details.innerHTML = error.stack;

  // Append elements
  messageBox.appendChild(closeButton);
  messageBox.appendChild(title);
  messageBox.appendChild(details);
  overlay.appendChild(messageBox);
  document.body.appendChild(overlay);

  // Add styles using JavaScript
  overlay.style.position = "fixed";
  overlay.style.top = "0";
  overlay.style.left = "0";
  overlay.style.width = "100%";
  overlay.style.height = "100%";
  overlay.style.backgroundColor = "rgba(0, 0, 0, 0.8)";
  overlay.style.color = "white";
  overlay.style.display = "flex";
  overlay.style.justifyContent = "center";
  overlay.style.alignItems = "center";
  overlay.style.zIndex = "1000";

  messageBox.style.background = "rgba(254, 226, 226,1)";
  messageBox.style.padding = "20px";
  messageBox.style.borderRadius = "5px";
  messageBox.style.maxWidth = "80%";
  messageBox.style.maxHeight = "80%";
  messageBox.style.overflow = "auto";
  messageBox.style.color = "rgb(185, 28, 28 ,1 )";

  title.style.marginTop = "0";

  details.style.whiteSpace = "pre-wrap";
  details.style.marginTop = "10px";

  closeButton.style.backgroundColor = "#ff5e5e";
  closeButton.style.border = "none";
  closeButton.style.borderRadius = "4px";
  closeButton.style.color = "white";
  closeButton.style.padding = "8px";
  closeButton.style.cursor = "pointer";
  closeButton.style.float = "right";

  closeButton.addEventListener("mouseover", () => {
    {
      closeButton.style.backgroundColor = "#ff1e1e";
    }
  });

  closeButton.addEventListener("mouseout", () => {
    {
      closeButton.style.backgroundColor = "#ff5e5e";
    }
  });

  // Close button functionality
  closeButton.addEventListener("click", () => {
    overlay.style.display = "none";
  });
  throw new Error(error);

  // Run your specific function here
  // e.g., log to a service, display a fallback UI, etc.
}

const container = document.getElementById("root");

window.__REACT_HYDRATE__ = function (url) {
  if (!container) return;
  hydrateRoot(
    container,
    <React.StrictMode>
      <Router>
        <App {...getServerProps({})} />
      </Router>
    </React.StrictMode>,
    { onRecoverableError: handleHydrationError }
  );
};

window.__REACT_HYDRATE__();

// Function to handle navigation events
function handleNavigation(event) {
  if (event.state !== null) {
    window.fastApi_react_app_props = event.state;
  }
  // Run your custom function here based on the navigation state
}

document.addEventListener("DOMContentLoaded", function () {
  // Define your initial state object
  const initialState = window.fastApi_react_app_props;

  // Replace or push state as needed
  history.replaceState(initialState, document.title, window.location.href);

  // Optionally, dispatch a popstate event to notify the app of the initial state
  window.dispatchEvent(new PopStateEvent("popstate", { state: initialState }));

  // Add event listener for 'popstate' events
  window.addEventListener("popstate", handleNavigation);
});
