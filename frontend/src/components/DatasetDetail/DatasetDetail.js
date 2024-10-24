// src/components/DatasetDetail/DatasetDetail.js
import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { Link, useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { Alert } from 'react-bootstrap';
import { datasetService, getErrorMessage } from '../../services/api';
import Summary from '../Summary/Summary';
import ClinicalData from '../ClinicalData/ClinicalData';
import Analysis from '../Analysis/Analysis';
import Heatmap from '../Heatmap/Heatmap';
import PageLoading from '../ui/PageLoading';
import './DatasetDetail.css';

const TABS = [
  { id: 'summary', label: 'Summary' },
  { id: 'clinical', label: 'Clinical Data' },
  { id: 'analysis', label: 'Analysis' },
  { id: 'heatmap', label: 'Heatmap' },
];

const VALID_TAB_IDS = new Set(TABS.map((t) => t.id));

const DatasetDetail = () => {
  const { datasetId } = useParams();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [dataset, setDataset] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dataStatus, setDataStatus] = useState(null);

  const activeTab = useMemo(() => {
    const raw = searchParams.get('tab');
    if (raw && VALID_TAB_IDS.has(raw)) {
      return raw;
    }
    return 'summary';
  }, [searchParams]);

  const setActiveTab = useCallback(
    (id) => {
      setSearchParams(
        (prev) => {
          const next = new URLSearchParams(prev);
          if (id === 'summary') {
            next.delete('tab');
          } else {
            next.set('tab', id);
          }
          return next;
        },
        { replace: true },
      );
    },
    [setSearchParams],
  );

  const tabAvailability = useMemo(() => {
    if (!dataStatus) {
      return {
        summary: true,
        clinical: true,
        analysis: true,
        heatmap: true,
      };
    }
    return {
      summary: Boolean(dataStatus.summary_ready),
      clinical: Boolean(dataStatus.clinical_patient_ingested),
      analysis: Boolean(dataStatus.clinical_patient_ingested),
      heatmap: Boolean(dataStatus.expression_matrix_source_present),
    };
  }, [dataStatus]);

  useEffect(() => {
    if (!dataStatus) return;
    const ok = tabAvailability;
    if (ok[activeTab]) return;
    const order = ['clinical', 'summary', 'analysis', 'heatmap'];
    const next = order.find((id) => ok[id]);
    if (next && next !== activeTab) {
      setActiveTab(next);
    }
  }, [dataStatus, activeTab, tabAvailability, setActiveTab]);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      setLoading(true);
      setError(null);
      setDataset(null);
      setDataStatus(null);
      try {
        const meta = await datasetService.getDatasetMeta(datasetId);
        if (cancelled) return;
        if (!meta) {
          setError(null);
          setDataset(null);
        } else {
          setDataset(meta);
          try {
            const st = await datasetService.getStudyDataStatus(datasetId);
            if (!cancelled) {
              setDataStatus(st);
            }
          } catch {
            if (!cancelled) {
              setDataStatus(null);
            }
          }
        }
      } catch (err) {
        if (!cancelled) {
          setError(getErrorMessage(err, 'Failed to load datasets'));
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    load();
    return () => {
      cancelled = true;
    };
  }, [datasetId]);

  if (loading) {
    return <PageLoading message="Loading study…" />;
  }
  if (error) {
    return (
      <Alert variant="danger" className="mt-3" role="alert">
        {error}
      </Alert>
    );
  }
  if (!dataset) {
    return (
      <Alert variant="warning" className="mt-3" role="alert">
        <Alert.Heading className="h5">Dataset not found</Alert.Heading>
        <p className="mb-0">
          No study matches <code>{datasetId}</code> in the catalog.
        </p>
      </Alert>
    );
  }

  return (
    <div className={`dataset-detail ${activeTab === 'summary' ? 'summary-active' : ''}`}>
      {activeTab !== 'summary' && (
        <div className="dataset-header-card">
          <Link to="/" className="back-link">
            ← All datasets
          </Link>
          <h1 className="dataset-title">{dataset.name}</h1>
          <p className="dataset-type">{dataset.type}</p>
          {dataStatus && (
            <section className="dataset-status-panel" role="status" aria-label="Data plane status">
              <h2>Data Plane Status</h2>
              <div className="dataset-status-grid">
                <div className="status-item">
                  <span>Clinical patient</span>
                  <strong>{dataStatus.clinical_patient_ingested ? 'Ready' : 'Missing'}</strong>
                </div>
                <div className="status-item">
                  <span>Clinical sample</span>
                  <strong>{dataStatus.clinical_sample_ingested ? 'Ready' : 'Missing'}</strong>
                </div>
                <div className="status-item">
                  <span>Mutations table</span>
                  <strong>{dataStatus.mutations_table ? 'Ready' : 'Missing'}</strong>
                </div>
                <div className="status-item">
                  <span>GISTIC table</span>
                  <strong>{dataStatus.gistic_table ? 'Ready' : 'Missing'}</strong>
                </div>
                <div className="status-item">
                  <span>Summary tab</span>
                  <strong>{dataStatus.summary_ready ? 'Ready' : 'Not ready'}</strong>
                </div>
                <div className="status-item">
                  <span>Heatmap source</span>
                  <strong>{dataStatus.expression_matrix_source_present ? 'Ready' : 'Missing'}</strong>
                </div>
              </div>
            </section>
          )}

          <p className="dataset-jobs-link mb-3">
            <button
              type="button"
              className="btn btn-link p-0 align-baseline"
              onClick={() =>
                navigate(`/jobs?study=${encodeURIComponent(dataset.id)}`)
              }
            >
              Async jobs for this study
            </button>
          </p>
        </div>
      )}

      <div
        className="tabs"
        role="tablist"
        aria-label="Study sections"
      >
        {TABS.map((tab) => {
          const enabled = tabAvailability[tab.id];
          const title = !enabled
            ? 'Not available for this study (see data plane status above).'
            : undefined;
          return (
            <button
              key={tab.id}
              type="button"
              role="tab"
              id={`tab-${tab.id}`}
              title={title}
              aria-selected={activeTab === tab.id}
              aria-controls={`panel-${tab.id}`}
              tabIndex={activeTab === tab.id ? 0 : -1}
              disabled={!enabled}
              className={activeTab === tab.id ? 'active' : ''}
              onClick={() => enabled && setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          );
        })}
      </div>

      <div className={`tab-content ${activeTab === 'summary' ? 'tab-content-summary' : ''}`}>
        {activeTab === 'summary' && (
          <div
            role="tabpanel"
            id="panel-summary"
            aria-labelledby="tab-summary"
          >
            <Summary datasetId={datasetId} />
          </div>
        )}
        {activeTab === 'clinical' && (
          <div
            role="tabpanel"
            id="panel-clinical"
            aria-labelledby="tab-clinical"
          >
            <ClinicalData datasetId={datasetId} />
          </div>
        )}
        {activeTab === 'analysis' && (
          <div
            role="tabpanel"
            id="panel-analysis"
            aria-labelledby="tab-analysis"
          >
            <Analysis datasetId={datasetId} />
          </div>
        )}
        {activeTab === 'heatmap' && (
          <div
            role="tabpanel"
            id="panel-heatmap"
            aria-labelledby="tab-heatmap"
          >
            <Heatmap datasetId={datasetId} />
          </div>
        )}
      </div>
    </div>
  );
};

export default DatasetDetail;
