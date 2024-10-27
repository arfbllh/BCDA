import React from 'react';
import { Link } from 'react-router-dom';

export default function Help() {
  return (
    <div className="app-page">
      <p className="app-link-row">
        <Link to="/">← Home</Link>
      </p>
      <section className="app-hero">
        <h1>Help</h1>
        <p>Quick usage guide for datasets, analysis, heatmap, and async jobs.</p>
      </section>
      <section className="app-card p-4 content-prose">
      <ul className="space-y-3">
        <li>
          <strong>Datasets</strong> — Choose a study from the home page. Study headers come
          from the grouped catalog API (there is no separate “dataset detail” endpoint).
          Open a specific tab with the query parameter <code>tab</code>:{' '}
          <code>summary</code>, <code>clinical</code>, <code>analysis</code>, or{' '}
          <code>heatmap</code> (for example <code>?tab=heatmap</code>).
        </li>
        <li>
          <strong>Clinical table</strong> — Rows are loaded in pages from the server. Text
          filters apply only to the current page; clear filters and change pages to scan more
          patients.
        </li>
        <li>
          <strong>Heatmap</strong> — Loads{' '}
          <code>data_mrna_seq_v2_rsem_zscores_ref_all_samples.csv</code> for the study in the URL
          from <code>DATASETS_BASE_DIR</code> on the server (subset of rows/columns for performance).
        </li>
        <li>
          <strong>Async jobs</strong> — Use the <Link to="/jobs">Jobs</Link> page to submit{' '}
          <code>POST /api/v1/analysis/jobs</code> and poll for results. Celery workers must be
          running or jobs stay queued.
        </li>
        <li>
          <strong>OpenAPI</strong> — See <Link to="/api-docs">API docs</Link> for the JSON spec
          returned by <code>/api/v1/openapi.json</code> (subset of routes may be listed).
        </li>
        <li>
          <strong>API base URL</strong> — See the Frontend section in repo-root{' '}
          <code>.env.example</code>; copy values into <code>frontend/.env.local</code> for{' '}
          <code>REACT_APP_API_BASE_URL</code>. Production deployments should set CORS on the
          API for your browser origin.
        </li>
      </ul>
      </section>
    </div>
  );
}
