// import React from "react";
// import { Link, useLocation, useNavigate } from "react-router-dom";
// import "./Navbar.css";

// const Navbar = () => {
//   const location = useLocation();
//   const navigate = useNavigate();

//   // Hide Navbar on login or register pages
//   if (location.pathname === "/login" || location.pathname === "/register") {
//     return null;
//   }

//   const isActive = (path) => location.pathname === path;

//   const handleLogout = () => {
//     // Remove stored token or session info
//     localStorage.removeItem("token");
//     // Redirect user to login page
//     navigate("/login");
//   };

//   return (
//     <nav className="navbar">
//       {/* Brand Logo */}
//       <Link to="/" className="navbar-logo">
//         🎓 AI Tutor
//       </Link>

//       {/* Navigation Links */}
//       <div className="navbar-links">
//         <Link to="/" className={isActive("/") ? "active-link" : ""}>
//           Home
//         </Link>

//         <Link to="/chat" className={isActive("/chat") ? "active-link" : ""}>
//           Chat
//         </Link>

//         <Link
//           to="/explanation"
//           className={isActive("/explanation") ? "active-link" : ""}
//         >
//           Explanation
//         </Link>

//         <Link
//           to="/learning-path"
//           className={isActive("/learning-path") ? "active-link" : ""}
//         >
//           Learning Path
//         </Link>

//         <Link
//           to="/analytics"
//           className={isActive("/analytics") ? "active-link" : ""}
//         >
//           Analytics
//         </Link>

//         <Link to="/quiz" className={isActive("/quiz") ? "active-link" : ""}>
//           Quiz
//         </Link>

//         <Link
//           to="/profile"
//           className={isActive("/profile") ? "active-link" : ""}
//         >
//           Profile
//         </Link>

//         {/* Logout Button */}
//         <button className="logout-btn" onClick={handleLogout}>
//           Logout
//         </button>
//       </div>
//     </nav>
//   );
// };

// export default Navbar;


import React from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import "./Navbar.css";

const Navbar = () => {
  const location = useLocation();
  const navigate = useNavigate();

  // Hide Navbar on login or register pages
  if (location.pathname === "/login" || location.pathname === "/register") {
    return null;
  }

  const isActive = (path) => location.pathname === path;

  const handleLogout = () => {
    // Remove stored token or session info
    localStorage.removeItem("token");
    // Redirect user to login page
    navigate("/login");
  };

  return (
    <nav className="navbar">
      {/* Brand Logo */}
      <div className="navbar-brand">
        <div className="logo-container">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="32" height="32" rx="8" fill="#6e4ff5"/>
            <path d="M16 8L8 12V16H24V12L16 8Z" fill="white"/>
            <path d="M8 16L16 20L24 16" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
        <span className="brand-name">AI Tutor</span>
      </div>

      {/* Navigation Links */}
      <div className="navbar-links">
        <Link to="/" className={`nav-link ${isActive("/") ? "active" : ""}`}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M9 22V12h6v10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Home
        </Link>

        <Link to="/chat" className={`nav-link ${isActive("/chat") ? "active" : ""}`}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M8 12h8v4H8v-4z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10c5.52 0 10-4.48 10-10S17.52 2 12 2zm0 2c2.67 0 8 1.34 8 4v6H4v-6c0-2.66 5.33-4 8-4z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Chat
        </Link>

        <Link to="/explanation" className={`nav-link ${isActive("/explanation") ? "active" : ""}`}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 6.253v13m0-13C10.832 5.456 9.247 5 7.5 5S4.168 5.456 3 6.253v13C4.168 18.456 5.753 18 7.5 18s3.332.456 4.5 1.253v-13z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Explanation
        </Link>

        <Link to="/learning-path" className={`nav-link ${isActive("/learning-path") ? "active" : ""}`}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9M9 9a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm12-2a2 2 0 00-2-2h-2a2 2 0 00-2 2v14a2 2 0 002 2h2a2 2 0 002-2V9z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Learning Path
        </Link>

        <Link to="/analytics" className={`nav-link ${isActive("/analytics") ? "active" : ""}`}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9M9 9a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm12-2a2 2 0 00-2-2h-2a2 2 0 00-2 2v14a2 2 0 002 2h2a2 2 0 002-2V9z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Analytics
        </Link>

        <Link to="/quiz" className={`nav-link ${isActive("/quiz") ? "active" : ""}`}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M8.228 9c-.549-1.169-2.03-2-3.228-2S3 7.831 2.451 9C1.872 10.169 1 11.434 1 13c0 1.566.872 2.831 1.451 4.001C3 18.169 4.48 19 5.678 19S8.228 18.169 8.228 17c0-1.566-.872-2.831-1.451-4.001C6.2 11.831 7.68 10.169 8.228 9zM12 18c0 1.566.872 2.831 1.451 4.001C13.8 23.169 15.28 24 16.478 24S19.17 23.169 19.75 22c0-1.566-.872-2.831-1.451-4.001C17.8 16.831 16.32 15.169 15.772 14c-.549-1.169-2.03-2-3.228-2S10.5 12.831 9.951 14c-.549 1.169-2.03 2-3.228 2S5 17.831 5.551 19C6.1 20.169 7.58 21 8.778 21S10.47 20.169 11 19c0-1.566.872-2.831 1.451-4.001C12.8 13.831 14.28 12.169 14.828 11c.549-1.169 2.03-2 3.228-2S19.5 9.831 20.051 11C20.6 12.169 22.08 13 23.278 13S24.97 12.169 25.5 11c0-1.566-.872-2.831-1.451-4.001C23.5 5.831 22.02 4 20.828 4S19.17 5.831 18.772 7c-.549 1.169-2.03 2-3.228 2S14.5 8.169 14 7c0-1.566-.872-2.831-1.451-4.001C12.2 1.831 10.72 0 9.528 0S7.83 1.831 7.272 3c-.549 1.169-2.03 2-3.228 2S2.5 4.169 2 3c0-1.566-.872-2.831-1.451-4.001C0.2 0.169 0 0 0 0s0 0 0 0z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Quiz
        </Link>

        <Link to="/profile" className={`nav-link ${isActive("/profile") ? "active" : ""}`}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Profile
        </Link>

        <button className="logout-btn" onClick={handleLogout}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M17 16l4-4m0 0l-4-4m4 4H7m6 6v-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Logout
        </button>
      </div>
    </nav>
  );
};

export default Navbar;