// src/components/Navbar/Navbar.js
import React from 'react';
import { Link, NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './Navbar.css';

const Navbar = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const linkClass = ({ isActive }) =>
    `nav-link${isActive ? ' active' : ''}`;

  return (
    <nav className="navbar" role="navigation" aria-label="Main">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          BCancerPortal
        </Link>
        <ul className="nav-menu">
          <li className="nav-item">
            <NavLink to="/" className={linkClass} end>
              Home
            </NavLink>
          </li>
          <li className="nav-item">
            <NavLink to="/jobs" className={linkClass}>
              Jobs
            </NavLink>
          </li>
          <li className="nav-item">
            <NavLink to="/upload" className={linkClass}>
              Upload
            </NavLink>
          </li>
          <li className="nav-item">
            <NavLink to="/assistant" className={linkClass}>
              Assistant
            </NavLink>
          </li>
          <li className="nav-item">
            <NavLink to="/api-docs" className={linkClass}>
              API
            </NavLink>
          </li>
          <li className="nav-item">
            <NavLink to="/about" className={linkClass}>
              About
            </NavLink>
          </li>
          <li className="nav-item">
            {isAuthenticated ? (
              <button type="button" className="nav-link nav-button" onClick={logout}>
                Logout ({user?.full_name || user?.email})
              </button>
            ) : (
              <NavLink to="/login" className={linkClass}>
                Login
              </NavLink>
            )}
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;
