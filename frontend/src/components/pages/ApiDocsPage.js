import React, { useState, useEffect, useMemo } from 'react';
import { Alert, Button, Spinner } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { fetchOpenApiSpec, getApiBaseUrl, getErrorMessage } from '../../services/api';
import './ApiDocsPage.css';

export default function ApiDocsPage() {
  const [spec, setSpec] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [copyDone, setCopyDone] = useState(false);

  const rawUrl = useMemo(() => {
    const base = getApiBaseUrl().replace(/\/$/, '');
    if (base.startsWith('http')) {
      return `${base}/openapi.json`;
    }
    const path = base.startsWith('/') ? base : `/${base}`;
    return `${window.location.origin}${path}/openapi.json`;
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchOpenApiSpec();
        if (!cancelled) setSpec(data);
      } catch (e) {
        if (!cancelled) setError(getErrorMessage(e, 'Could not load OpenAPI document'));
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const handleCopy = async () => {
    if (!spec) return;
    try {
      await navigator.clipboard.writeText(JSON.stringify(spec, null, 2));
      setCopyDone(true);
      setTimeout(() => setCopyDone(false), 2000);
    } catch {
      setError('Clipboard not available. Use “Open raw JSON” and copy from the new tab.');
    }
  };

  return (
    <div className="api-docs-page app-page">
      <p className="app-link-row">
        <Link to="/">← Home</Link>
      </p>
      <section className="app-hero">
        <h1>API Reference</h1>
        <p>
          Loads <code>GET /api/v1/openapi.json</code> from <code>{getApiBaseUrl()}</code>.
        </p>
      </section>

      <div className="api-docs-toolbar app-card p-3">
        <Button
          href={rawUrl}
          target="_blank"
          rel="noopener noreferrer"
          variant="outline-primary"
          size="sm"
        >
          Open raw JSON
        </Button>
        <Button
          type="button"
          variant="outline-secondary"
          size="sm"
          onClick={handleCopy}
          disabled={!spec}
        >
          {copyDone ? 'Copied' : 'Copy JSON'}
        </Button>
      </div>

      {loading && (
        <div className="py-5 text-center">
          <Spinner animation="border" role="status" />
          <span className="visually-hidden">Loading</span>
        </div>
      )}
      {error && (
        <Alert variant="danger" className="mt-3">
          {error}
        </Alert>
      )}
      {!loading && !error && spec && (
        <pre className="api-docs-spec">{JSON.stringify(spec, null, 2)}</pre>
      )}
    </div>
  );
}
