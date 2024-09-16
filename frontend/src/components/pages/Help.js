import React from 'react';
import { Container } from 'react-bootstrap';
import { Link } from 'react-router-dom';

export default function Help() {
  return (
    <Container className="py-4 app-static-page">
      <p className="mb-3">
        <Link to="/">← Home</Link>
      </p>
      <h1 className="h2 mb-3">Help</h1>
      <ul>
        <li>
          <strong>Datasets</strong> — Choose a study from the home page. Study headers come
          from the grouped catalog API (there is no separate “dataset detail” endpoint).
        </li>
        <li>
          <strong>Clinical table</strong> — Rows are loaded in pages from the server. Text
          filters apply only to the current page; clear filters and change pages to scan more
          patients.
        </li>
        <li>
          <strong>Heatmap</strong> — The API currently returns a fixed TCGA matrix slice; the
          plot does not yet change per study.
        </li>
        <li>
          <strong>API base URL</strong> — See <code>frontend/.env.example</code> for{' '}
          <code>REACT_APP_API_BASE_URL</code>. Production deployments should set CORS on the
          API for your browser origin.
        </li>
      </ul>
    </Container>
  );
}
