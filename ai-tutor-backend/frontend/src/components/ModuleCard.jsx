import React from "react";
import { Link } from "react-router-dom";

const ModuleCard = ({ title, description, route, color }) => {
  return (
    <Link to={route}>
      <div
        className="module-card"
        style={{ backgroundColor: color }}
      >
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </Link>
  );
};

export default ModuleCard;
