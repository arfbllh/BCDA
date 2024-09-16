// src/components/Navbar/Navbar.js
import React from 'react';
import { Link, NavLink } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
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
            <NavLink to="/about" className={linkClass}>
              About
            </NavLink>
          </li>
          <li className="nav-item">
            <NavLink to="/help" className={linkClass}>
              Help
            </NavLink>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;
