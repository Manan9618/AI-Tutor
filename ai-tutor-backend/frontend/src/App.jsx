// import React from "react";
// import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from "react-router-dom";
// import Navbar from "./components/Navbar";
// import Home from "./pages/Home";
// import Chat from "./pages/Chat";
// import Explanation from "./pages/Explanation";
// import LearningPath from "./pages/LearningPath";
// import Analytics from "./pages/Analytics";
// import Quiz from "./pages/Quiz";
// import LearnerProfile from "./pages/LearnerProfile";
// import NotFound from "./pages/NotFound";
// import Login from "./pages/Login";
// import Register from "./pages/Register";
// import "./index.css";

// /**
//  * PrivateRoute component — only allows access if user is logged in
//  */
// const PrivateRoute = ({ children }) => {
//   const isAuthenticated = localStorage.getItem("authToken");
//   return isAuthenticated ? children : <Navigate to="/login" />;
// };

// /**
//  * Layout component — hides Navbar on login/register pages
//  */
// const Layout = ({ children }) => {
//   const location = useLocation();
//   const hideNavbar = ["/login", "/register"].includes(location.pathname);
//   return (
//     <div className="app-container">
//       {!hideNavbar && <Navbar />}
//       {children}
//     </div>
//   );
// };

// /**
//  * Main App Component for AI Tutor Frontend
//  * - Manages all frontend routes
//  * - Integrates Navbar conditionally
//  * - Enforces login/register before accessing main app
//  */
// const App = () => {
//   return (
//     <Router>
//       <Layout>
//         <Routes>
//           {/* Auth Pages */}
//           <Route path="/login" element={<Login />} />
//           <Route path="/register" element={<Register />} />

//           {/* Protected Routes */}
//           <Route
//             path="/"
//             element={
//               <PrivateRoute>
//                 <Home />
//               </PrivateRoute>
//             }
//           />
//           <Route
//             path="/chat"
//             element={
//               <PrivateRoute>
//                 <Chat />
//               </PrivateRoute>
//             }
//           />
//           <Route
//             path="/explanation"
//             element={
//               <PrivateRoute>
//                 <Explanation />
//               </PrivateRoute>
//             }
//           />
//           <Route
//             path="/learning-path"
//             element={
//               <PrivateRoute>
//                 <LearningPath />
//               </PrivateRoute>
//             }
//           />
//           <Route
//             path="/analytics"
//             element={
//               <PrivateRoute>
//                 <Analytics />
//               </PrivateRoute>
//             }
//           />
//           <Route
//             path="/quiz"
//             element={
//               <PrivateRoute>
//                 <Quiz />
//               </PrivateRoute>
//             }
//           />
//           <Route
//             path="/profile"
//             element={
//               <PrivateRoute>
//                 <LearnerProfile />
//               </PrivateRoute>
//             }
//           />

//           {/* Catch-all for 404s */}
//           <Route path="*" element={<NotFound />} />
//         </Routes>
//       </Layout>
//     </Router>
//   );
// };

// export default App;


import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Chat from "./pages/Chat";
import Explanation from "./pages/Explanation";
import LearningPath from "./pages/LearningPath";
import Analytics from "./pages/Analytics";
import Quiz from "./pages/Quiz";
import LearnerProfile from "./pages/LearnerProfile";
import NotFound from "./pages/NotFound";
import Login from "./pages/Login";
import Register from "./pages/Register";
import "./index.css";

/**
 * PrivateRoute component — only allows access if user is logged in
 */
const PrivateRoute = ({ children }) => {
  const isAuthenticated = localStorage.getItem("authToken");
  return isAuthenticated ? children : <Navigate to="/login" />;
};

/**
 * Layout component — hides Navbar on login/register pages
 */
const Layout = ({ children }) => {
  const location = useLocation();
  const hideNavbar = ["/login", "/register"].includes(location.pathname);
  return (
    <div className="app-container">
      {!hideNavbar && <Navbar />}
      {children}
    </div>
  );
};

/**
 * Main App Component for AI Tutor Frontend
 * - Manages all frontend routes
 * - Integrates Navbar conditionally
 * - Enforces login/register before accessing main app
 */
const App = () => {
  return (
    <Router>
      <Layout>
        <Routes>
          {/* Auth Pages */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protected Routes */}
          <Route
            path="/"
            element={
              <PrivateRoute>
                <Home />
              </PrivateRoute>
            }
          />
          <Route
            path="/chat"
            element={
              <PrivateRoute>
                <Chat />
              </PrivateRoute>
            }
          />
          <Route
            path="/explanation"
            element={
              <PrivateRoute>
                <Explanation />
              </PrivateRoute>
            }
          />
          <Route
            path="/learning-path"
            element={
              <PrivateRoute>
                <LearningPath />
              </PrivateRoute>
            }
          />
          <Route
            path="/analytics"
            element={
              <PrivateRoute>
                <Analytics />
              </PrivateRoute>
            }
          />
          <Route
            path="/quiz"
            element={
              <PrivateRoute>
                <Quiz />
              </PrivateRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <PrivateRoute>
                <LearnerProfile />
              </PrivateRoute>
            }
          />

          {/* Catch-all for 404s */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Layout>
    </Router>
  );
};

export default App;