// src/components/Navbar/Navbar.js
import React from 'react';
import { Link, NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const Navbar = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const linkClass = ({ isActive }) =>
    `px-3 py-2 rounded-lg text-sm font-semibold transition ${
      isActive
        ? 'bg-blue-100 text-blue-700 shadow-sm'
        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
    }`;

  return (
    <nav className="sticky top-0 z-50 border-b border-slate-200/80 bg-white/85 backdrop-blur-xl" role="navigation" aria-label="Main">
      <div className="mx-auto flex h-16 w-[94%] max-w-7xl items-center justify-between">
        <Link to="/" className="text-lg font-extrabold tracking-tight text-slate-900">
          BCancerPortal
        </Link>
        <ul className="flex items-center gap-1">
          <li>
            <NavLink to="/" className={linkClass} end>
              Home
            </NavLink>
          </li>
          <li>
            <NavLink to="/jobs" className={linkClass}>
              Jobs
            </NavLink>
          </li>
          <li>
            <NavLink to="/upload" className={linkClass}>
              Upload
            </NavLink>
          </li>
          <li>
            <NavLink to="/assistant" className={linkClass}>
              Assistant
            </NavLink>
          </li>
          <li>
            <NavLink to="/api-docs" className={linkClass}>
              API
            </NavLink>
          </li>
          <li>
            <NavLink to="/about" className={linkClass}>
              About
            </NavLink>
          </li>
          <li>
            {isAuthenticated ? (
              <button
                type="button"
                className="rounded-lg bg-slate-900 px-3 py-2 text-sm font-semibold text-white hover:bg-slate-800"
                onClick={logout}
              >
                Logout
              </button>
            ) : (
              <NavLink to="/login" className={linkClass}>
                Login
              </NavLink>
            )}
          </li>
          {isAuthenticated && (
            <li className="ml-2 hidden text-xs text-slate-500 md:block">
              {user?.full_name || user?.email}
            </li>
          )}
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;
