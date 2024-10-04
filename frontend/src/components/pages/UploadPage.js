import React, { useState } from 'react';
import { Alert, Button, Card, Form } from 'react-bootstrap';
import { uploadService, getErrorMessage } from '../../services/api';

export default function UploadPage() {
  const [studyId, setStudyId] = useState('');
  const [file, setFile] = useState(null);
  const [upload, setUpload] = useState(null);
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  const doUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Select a .zip file first.');
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const res = await uploadService.createUpload({ studyId, file });
      setUpload(res);
      setStatus(null);
    } catch (err) {
      setError(getErrorMessage(err, 'Upload failed'));
    } finally {
      setBusy(false);
    }
  };

  const startIngest = async () => {
    if (!upload?.upload_id) return;
    setBusy(true);
    try {
      await uploadService.triggerIngest(upload.upload_id);
      const st = await uploadService.getUploadStatus(upload.upload_id);
      setStatus(st);
    } catch (err) {
      setError(getErrorMessage(err, 'Could not trigger ingestion'));
    } finally {
      setBusy(false);
    }
  };

  const refreshStatus = async () => {
    if (!upload?.upload_id) return;
    setBusy(true);
    try {
      const st = await uploadService.getUploadStatus(upload.upload_id);
      setStatus(st);
    } catch (err) {
      setError(getErrorMessage(err, 'Could not refresh status'));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="app-static-page">
      <h1 className="h3 mb-3">Upload dataset bundle</h1>
      <p className="text-muted">
        Upload a study .zip bundle, then trigger ingestion to load it into the platform.
      </p>
      <Card className="mb-3">
        <Card.Body>
          <Form onSubmit={doUpload}>
            <Form.Group className="mb-3">
              <Form.Label>Study ID</Form.Label>
              <Form.Control
                value={studyId}
                onChange={(e) => setStudyId(e.target.value)}
                placeholder="e.g. brca_sanger"
                required
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Bundle (.zip)</Form.Label>
              <Form.Control
                type="file"
                accept=".zip"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                required
              />
            </Form.Group>
            {error && <Alert variant="danger">{error}</Alert>}
            <Button type="submit" disabled={busy}>
              {busy ? 'Working...' : 'Upload'}
            </Button>
          </Form>
        </Card.Body>
      </Card>
      {upload && (
        <Card>
          <Card.Body>
            <p className="mb-1">
              Upload ID: <code>{upload.upload_id}</code>
            </p>
            <p className="mb-3">
              Status: <strong>{status?.status || upload.status}</strong>
            </p>
            <div className="d-flex gap-2">
              <Button variant="primary" onClick={startIngest} disabled={busy}>
                Start ingestion
              </Button>
              <Button variant="outline-secondary" onClick={refreshStatus} disabled={busy}>
                Refresh status
              </Button>
            </div>
            {status?.error_message && (
              <Alert className="mt-3 mb-0" variant="warning">
                {status.error_message}
              </Alert>
            )}
          </Card.Body>
        </Card>
      )}
    </div>
  );
}
