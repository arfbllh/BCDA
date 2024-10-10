import React from 'react';
import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="mt-auto border-t border-slate-200 bg-white">
      <div className="mx-auto flex w-[94%] max-w-6xl items-center justify-between gap-4 py-6">
        <div>
          <strong className="text-slate-900">BCancerPortal</strong>
          <p className="mb-0 text-sm text-slate-500">
            Genomics exploration, ML analytics, and upload workflows.
          </p>
        </div>
        <nav className="flex gap-4 text-sm" aria-label="Footer links">
          <Link className="text-slate-600 hover:text-slate-900" to="/about">About</Link>
          <Link className="text-slate-600 hover:text-slate-900" to="/help">Help</Link>
          <Link className="text-slate-600 hover:text-slate-900" to="/api-docs">API Docs</Link>
          <Link className="text-slate-600 hover:text-slate-900" to="/assistant">AI Assistant</Link>
        </nav>
      </div>
    </footer>
  );
}
