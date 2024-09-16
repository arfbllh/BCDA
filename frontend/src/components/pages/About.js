import React from 'react';
import { Container } from 'react-bootstrap';
import { Link } from 'react-router-dom';

export default function About() {
  return (
    <Container className="py-4 app-static-page">
      <p className="mb-3">
        <Link to="/">← Home</Link>
      </p>
      <h1 className="h2 mb-3">About BCancerPortal</h1>
      <p>
        BCancerPortal is a cBioPortal-inspired stack for exploring breast-cancer-focused
        studies: a Flask API plus this React app. Studies, clinical tables, summaries, and
        analysis endpoints are documented in the repository README and{' '}
        <code>doc/</code> at the project root.
      </p>
      <p>
        The UI calls versioned APIs under <code>/api/v1</code>. For local development, run
        the API (for example on port 4000) and start this app with the CRA proxy, or set{' '}
        <code>REACT_APP_API_BASE_URL</code> in <code>frontend/.env.local</code>.
      </p>
      <p>
        Browse the published OpenAPI JSON in the app: <Link to="/api-docs">API docs</Link>.
      </p>
    </Container>
  );
}
