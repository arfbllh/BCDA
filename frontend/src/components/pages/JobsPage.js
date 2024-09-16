import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Alert,
  Button,
  Card,
  Col,
  Form,
  Row,
  Spinner,
} from 'react-bootstrap';
import { Link, useSearchParams } from 'react-router-dom';
import {
  analysisJobService,
  getErrorMessage,
  pushRecentJob,
  readRecentJobIds,
} from '../../services/api';
import './JobsPage.css';

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

export default function JobsPage() {
  const [searchParams] = useSearchParams();
  const studyFromQuery = searchParams.get('study') || '';

  const [studyId, setStudyId] = useState(studyFromQuery);
  const [jobType, setJobType] = useState('generic');
  const [prompt, setPrompt] = useState('');
  const [maxTokens, setMaxTokens] = useState('');
  const [parametersJson, setParametersJson] = useState('{}');

  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);

  const [trackedJobId, setTrackedJobId] = useState('');
  const [pollPhase, setPollPhase] = useState('idle');
  const [pollError, setPollError] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);
  const [jobResult, setJobResult] = useState(null);

  const [recent, setRecent] = useState(() => readRecentJobIds());
  const [peek, setPeek] = useState(null);
  const cancelPoll = useRef(false);

  useEffect(() => {
    const s = searchParams.get('study');
    if (s) setStudyId(s);
  }, [searchParams]);

  const refreshRecent = useCallback(() => {
    setRecent(readRecentJobIds());
  }, []);

  const runPollLoop = useCallback(async (jobId) => {
    cancelPoll.current = false;
    setPollPhase('polling');
    setPollError(null);
    setJobStatus(null);
    setJobResult(null);

    let attempts = 0;
    const maxAttempts = 48;

    while (!cancelPoll.current && attempts < maxAttempts) {
      try {
        const status = await analysisJobService.getJob(jobId);
        if (cancelPoll.current) return;
        setJobStatus(status);

        if (status.status === 'failed') {
          setPollPhase('failed');
          setPollError(status.error_message || 'Job failed');
          return;
        }

        if (status.status === 'completed') {
          let rTries = 0;
          while (!cancelPoll.current && rTries < 8) {
            const res = await analysisJobService.getJobResult(jobId);
            if (cancelPoll.current) return;
            if (res.ready) {
              setJobResult(res.data);
              setPollPhase('done');
              return;
            }
            rTries += 1;
            await sleep(400);
          }
          if (!cancelPoll.current) {
            setPollPhase('failed');
            setPollError('Job completed but result endpoint did not return data yet.');
          }
          return;
        }

        const delay = Math.min(12000, 800 + attempts * 350);
        attempts += 1;
        await sleep(delay);
      } catch (e) {
        if (!cancelPoll.current) {
          setPollPhase('failed');
          setPollError(getErrorMessage(e, 'Polling failed'));
        }
        return;
      }
    }

    if (!cancelPoll.current) {
      setPollPhase('timeout');
      setPollError(
        'Stopped polling after many attempts. The job may still be running — refresh status or check workers.'
      );
    }
  }, []);

  useEffect(() => {
    if (!trackedJobId) return undefined;
    cancelPoll.current = false;
    runPollLoop(trackedJobId);
    return () => {
      cancelPoll.current = true;
    };
  }, [trackedJobId, runPollLoop]);

  const buildParameters = () => {
    if (jobType === 'llm_infer') {
      const params = {};
      if (prompt.trim()) params.prompt = prompt.trim();
      if (maxTokens.trim() !== '') {
        const n = parseInt(maxTokens, 10);
        if (!Number.isNaN(n)) params.max_tokens = n;
      }
      return params;
    }
    try {
      const parsed = JSON.parse(parametersJson || '{}');
      return typeof parsed === 'object' && parsed !== null ? parsed : {};
    } catch {
      throw new Error('Parameters must be valid JSON for non–LLM job types.');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitError(null);
    setSubmitting(true);
    setTrackedJobId('');
    setPollPhase('idle');
    setJobStatus(null);
    setJobResult(null);
    setPollError(null);
    setPeek(null);

    try {
      const parameters = buildParameters();
      const created = await analysisJobService.createJob({
        study_id: studyId.trim(),
        job_type: jobType,
        parameters,
      });
      pushRecentJob({
        job_id: created.job_id,
        study_id: created.study_id,
        job_type: created.job_type,
      });
      refreshRecent();
      setTrackedJobId(created.job_id);
    } catch (err) {
      setSubmitError(getErrorMessage(err, 'Could not create job'));
    } finally {
      setSubmitting(false);
    }
  };

  const loadStatusOnly = async (jobId) => {
    setPollError(null);
    try {
      const status = await analysisJobService.getJob(jobId);
      let resultPayload = null;
      if (status.status === 'completed') {
        const res = await analysisJobService.getJobResult(jobId);
        if (res.ready) resultPayload = res.data;
      }
      setPeek({ job_id: jobId, status, result: resultPayload });
    } catch (e) {
      setPeek({
        job_id: jobId,
        error: getErrorMessage(e, 'Could not load job'),
      });
    }
  };

  const resumeTracking = (jobId) => {
    setPeek(null);
    setTrackedJobId('');
    setTimeout(() => setTrackedJobId(jobId), 0);
  };

  return (
    <div className="jobs-page">
      <p className="mb-2">
        <Link to="/">← Home</Link>
        {studyFromQuery ? (
          <>
            {' · '}
            <Link to={`/datasets/${encodeURIComponent(studyFromQuery)}`}>
              Open study
            </Link>
          </>
        ) : null}
      </p>
      <h1>Async analysis jobs</h1>
      <p className="jobs-lead text-muted">
        Submit work to the API (<code>POST /api/v1/analysis/jobs</code>). A Celery worker must
        be running to move jobs past <code>queued</code>. Use <code>llm_infer</code> for optional
        LLM summaries when the backend is configured.
      </p>

      <Card className="jobs-form-card">
        <Card.Body>
          <Form onSubmit={handleSubmit}>
            <Row className="g-3 mb-3">
              <Col md={6}>
                <Form.Group controlId="job-study-id">
                  <Form.Label>Study ID</Form.Label>
                  <Form.Control
                    required
                    value={studyId}
                    onChange={(e) => setStudyId(e.target.value)}
                    placeholder="e.g. brca_tcga_pub2015"
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group controlId="job-type">
                  <Form.Label>Job type</Form.Label>
                  <Form.Select
                    value={jobType}
                    onChange={(e) => setJobType(e.target.value)}
                  >
                    <option value="generic">generic (placeholder result)</option>
                    <option value="llm_infer">llm_infer (optional LLM)</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>

            {jobType === 'llm_infer' ? (
              <Row className="g-3 mb-3">
                <Col xs={12}>
                  <Form.Group controlId="job-prompt">
                    <Form.Label>Prompt (optional)</Form.Label>
                    <Form.Control
                      as="textarea"
                      rows={3}
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                      placeholder="Leave blank to use the server default prompt."
                    />
                  </Form.Group>
                </Col>
                <Col md={4}>
                  <Form.Group controlId="job-max-tokens">
                    <Form.Label>max_tokens (optional)</Form.Label>
                    <Form.Control
                      type="number"
                      min={1}
                      value={maxTokens}
                      onChange={(e) => setMaxTokens(e.target.value)}
                      placeholder="512"
                    />
                  </Form.Group>
                </Col>
              </Row>
            ) : (
              <Form.Group className="mb-3" controlId="job-parameters-json">
                <Form.Label>Parameters (JSON object)</Form.Label>
                <Form.Control
                  as="textarea"
                  rows={4}
                  value={parametersJson}
                  onChange={(e) => setParametersJson(e.target.value)}
                  className="font-monospace"
                  spellCheck={false}
                />
              </Form.Group>
            )}

            {submitError && (
              <Alert variant="danger" className="mb-3">
                {submitError}
              </Alert>
            )}

            <Button type="submit" variant="primary" disabled={submitting}>
              {submitting ? (
                <>
                  <Spinner size="sm" className="me-2" animation="border" />
                  Submitting…
                </>
              ) : (
                'Submit job'
              )}
            </Button>
          </Form>
        </Card.Body>
      </Card>

      {trackedJobId && (
        <Card className="mb-3">
          <Card.Header>Current job</Card.Header>
          <Card.Body>
            <p className="mb-2">
              <strong>job_id:</strong> <code>{trackedJobId}</code>
            </p>
            {pollPhase === 'polling' && (
              <p className="text-muted mb-2">
                <Spinner size="sm" className="me-2" animation="border" />
                Waiting for worker…
              </p>
            )}
            {pollPhase === 'done' && (
              <Alert variant="success" className="mb-0">
                Job completed.
              </Alert>
            )}
            {(pollPhase === 'failed' || pollPhase === 'timeout') && pollError && (
              <Alert variant="warning">{pollError}</Alert>
            )}
            {jobStatus && (
              <div className="mt-2 small text-muted">
                status: <code>{jobStatus.status}</code>
                {jobStatus.queued_at && (
                  <>
                    {' · '}queued: {jobStatus.queued_at}
                  </>
                )}
                {jobStatus.started_at && (
                  <>
                    {' · '}started: {jobStatus.started_at}
                  </>
                )}
                {jobStatus.finished_at && (
                  <>
                    {' · '}finished: {jobStatus.finished_at}
                  </>
                )}
              </div>
            )}
            {jobResult && (
              <pre className="jobs-result-pre">
                {JSON.stringify(jobResult, null, 2)}
              </pre>
            )}
          </Card.Body>
        </Card>
      )}

      <Card>
        <Card.Header>Recent jobs (this browser)</Card.Header>
        <Card.Body>
          {recent.length === 0 ? (
            <p className="text-muted mb-0">No saved job IDs yet.</p>
          ) : (
            <ul className="jobs-recent-list">
              {recent.map((row) => (
                <li key={row.job_id}>
                  <code>{row.job_id}</code>
                  <span className="text-muted">{row.study_id}</span>
                  <Button
                    type="button"
                    variant="outline-secondary"
                    size="sm"
                    onClick={() => loadStatusOnly(row.job_id)}
                  >
                    Status
                  </Button>
                  <Button
                    type="button"
                    variant="outline-primary"
                    size="sm"
                    onClick={() => resumeTracking(row.job_id)}
                  >
                    Track
                  </Button>
                </li>
              ))}
            </ul>
          )}
          {peek && (
            <div className="mt-3 pt-3 border-top">
              <h3 className="h6">Selected job</h3>
              {peek.error ? (
                <Alert variant="danger" className="mb-0">
                  {peek.error}
                </Alert>
              ) : (
                <>
                  <p className="small mb-1">
                    <code>{peek.job_id}</code> —{' '}
                    <code>{peek.status?.status}</code>
                  </p>
                  {peek.status?.error_message && (
                    <Alert variant="warning">{peek.status.error_message}</Alert>
                  )}
                  {peek.result && (
                    <pre className="jobs-result-pre mb-0">
                      {JSON.stringify(peek.result, null, 2)}
                    </pre>
                  )}
                </>
              )}
            </div>
          )}
        </Card.Body>
      </Card>
    </div>
  );
}
