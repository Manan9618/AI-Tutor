// src/components/AppLayout.jsx
import React from "react";
import Navbar from "../components/Navbar";
import "./AppLayout.css";

const AppLayout = ({ children }) => {
  return (
    <div className="app-layout">
      <Navbar />
      <div className="content-wrapper">
        <div className="side-panel left-panel"></div>
        <div className="main-content">
          {children}
        </div>
        <div className="side-panel right-panel"></div>
      </div>
    </div>
  );
};

export default AppLayout;