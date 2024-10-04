import React from 'react';
import { Link } from 'react-router-dom';
import './Footer.css';

export default function Footer() {
  return (
    <footer className="app-footer">
      <div className="app-footer-inner">
        <div>
          <strong>BCancerPortal</strong>
          <p className="mb-0 small text-muted">Genomics exploration, ML analytics, and upload workflows.</p>
        </div>
        <nav className="app-footer-nav" aria-label="Footer links">
          <Link to="/about">About</Link>
          <Link to="/help">Help</Link>
          <Link to="/api-docs">API Docs</Link>
          <Link to="/assistant">AI Assistant</Link>
        </nav>
      </div>
    </footer>
  );
}
