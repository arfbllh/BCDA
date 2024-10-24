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

const JOB_TEMPLATES = {
  ml_risk: {
    title: 'Risk stratification demo',
    payload: {
      values: [0.21, 0.42, 0.37, 0.91, 0.84, 0.63, 0.15, 0.73],
    },
  },
  ml_feature: {
    title: 'Feature importance demo',
    payload: {
      pairs: [
        { feature: 'age', score: 0.34 },
        { feature: 'tumor_stage', score: 0.62 },
        { feature: 'tp53_mut', score: 0.47 },
        { feature: 'her2_status', score: 0.29 },
      ],
    },
  },
  ml_baseline: {
    title: 'Baseline metrics demo',
    payload: {
      metrics: {
        auc: 0.78,
        f1: 0.71,
        confusion_matrix: [[50, 12], [9, 44]],
      },
    },
  },
};

export default function JobsPage() {
  const [searchParams] = useSearchParams();
  const studyFromQuery = searchParams.get('study') || '';

  const [studyId, setStudyId] = useState(studyFromQuery);
  const [jobType, setJobType] = useState('ml_risk');
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

  const applyTemplate = (type) => {
    setJobType(type);
    const t = JOB_TEMPLATES[type];
    if (t) {
      setParametersJson(JSON.stringify(t.payload, null, 2));
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
    <div className="jobs-page app-page">
      <p className="app-link-row">
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
      <section className="app-hero">
        <h1>Async analysis jobs</h1>
        <p className="jobs-lead text-muted mb-0">
          Submit jobs to <code>POST /api/v1/analysis/jobs</code> and track result status.
          Use ML templates for risk, feature importance, and baseline metrics.
        </p>
      </section>

      <Card className="jobs-form-card app-card border-0 shadow-soft">
        <Card.Body>
          <h2 className="h5 mb-3">ML quick templates</h2>
          <div className="d-flex flex-wrap gap-2">
            <Button
              type="button"
              variant="outline-primary"
              onClick={() => applyTemplate('ml_risk')}
            >
              {JOB_TEMPLATES.ml_risk.title}
            </Button>
            <Button
              type="button"
              variant="outline-primary"
              onClick={() => applyTemplate('ml_feature')}
            >
              {JOB_TEMPLATES.ml_feature.title}
            </Button>
            <Button
              type="button"
              variant="outline-primary"
              onClick={() => applyTemplate('ml_baseline')}
            >
              {JOB_TEMPLATES.ml_baseline.title}
            </Button>
          </div>
          <p className="text-muted small mt-3 mb-0">
            These are working ML payload examples. Pick one, adjust values, then submit.
          </p>
        </Card.Body>
      </Card>

      <Card className="jobs-form-card app-card border-0 shadow-soft">
        <Card.Body>
          <Form onSubmit={handleSubmit}>
            <Row className="g-3 mb-3">
              <Col md={6}>
                <Form.Group controlId="job-study-id">
                  <Form.Label>Study ID</Form.Label>
                  <Form.Control
                    className="app-input"
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
                    className="app-select"
                    value={jobType}
                    onChange={(e) => setJobType(e.target.value)}
                  >
                    <option value="ml_risk">ml_risk (risk stratification)</option>
                    <option value="ml_feature">ml_feature (feature importance)</option>
                    <option value="ml_baseline">ml_baseline (AUC/F1 baseline)</option>
                    <option value="generic">generic</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>

            <Form.Group className="mb-3" controlId="job-parameters-json">
              <Form.Label>Parameters (JSON object)</Form.Label>
              <Form.Control
                as="textarea"
                className="font-monospace app-textarea"
                rows={4}
                value={parametersJson}
                onChange={(e) => setParametersJson(e.target.value)}
                spellCheck={false}
              />
            </Form.Group>

            {submitError && (
              <Alert variant="danger" className="mb-3">
                {submitError}
              </Alert>
            )}

            <Button type="submit" className="app-button-primary" disabled={submitting}>
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
        <Card className="mb-3 app-card border-0 shadow-soft">
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

      <Card className="app-card border-0 shadow-soft">
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
