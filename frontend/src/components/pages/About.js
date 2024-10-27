import React from 'react';
import { Link } from 'react-router-dom';

export default function About() {
  return (
    <div className="app-page">
      <p className="app-link-row">
        <Link to="/">← Home</Link>
      </p>
      <section className="app-hero">
        <h1>About BCancerPortal</h1>
        <p>
          A cBioPortal-inspired workspace for breast cancer study exploration, ML job workflows,
          and upload-driven ingestion.
        </p>
      </section>
      <section className="app-card p-4 content-prose space-y-3">
        <p>
          BCancerPortal combines a Flask API and React frontend for study browsing, clinical
          tables, summary dashboards, and async analytics.
        </p>
        <p>
          The UI calls versioned endpoints under <code>/api/v1</code>. For local development,
          run the backend and either use CRA proxy or configure <code>REACT_APP_API_BASE_URL</code>
          in <code>frontend/.env.local</code>.
        </p>
        <p className="mb-0">
          Browse the published OpenAPI JSON from <Link to="/api-docs">API docs</Link>.
        </p>
      </section>
    </div>
  );
}
