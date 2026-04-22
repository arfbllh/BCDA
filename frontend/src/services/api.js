// src/services/api.js
import axios from 'axios';

/**
 * Base URL for versioned API (no trailing slash).
 * Set REACT_APP_API_BASE_URL in frontend/.env.local (see repo-root .env.example, Frontend section).
 * Default /api/v1 works with package.json "proxy" to the Flask dev server.
 */
export function getApiBaseUrl() {
  const raw = process.env.REACT_APP_API_BASE_URL;
  if (raw != null && String(raw).trim() !== '') {
    return String(raw).trim().replace(/\/$/, '');
  }
  return '/api/v1';
}

function looksLikeTechnicalLeak(text) {
  if (typeof text !== 'string') return false;
  const t = text.toLowerCase();
  if (text.trimStart().startsWith('<!')) return true;
  return (
    t.includes('sqlalchemy') ||
    t.includes('pymysql') ||
    t.includes('traceback') ||
    t.includes('programmingerror') ||
    t.includes('operationalerror') ||
    t.includes('mysql server version for the right syntax')
  );
}

function formatEnvelopeMessage(inner) {
  if (inner == null) return null;
  if (typeof inner === 'string') {
    return looksLikeTechnicalLeak(inner) ? null : inner;
  }
  if (typeof inner === 'object' && inner.message != null) {
    if (typeof inner.message === 'string') {
      return looksLikeTechnicalLeak(inner.message) ? null : inner.message;
    }
    if (Array.isArray(inner.message)) {
      return inner.message
        .map((row) => {
          if (typeof row === 'string') return row;
          if (row && typeof row === 'object' && row.msg != null) {
            const loc = Array.isArray(row.loc) ? row.loc.filter(Boolean).join('.') : '';
            return loc ? `${loc}: ${row.msg}` : String(row.msg);
          }
          return JSON.stringify(row);
        })
        .join('; ');
    }
  }
  return null;
}

/**
 * Normalize Flask / axios errors for display.
 * Prefers api_error shape: { error: { code, message, request_id } }.
 * Avoids showing HTML error pages or raw DB tracebacks.
 */
export function getErrorMessage(error, fallback = 'Something went wrong') {
  if (error == null) return fallback;
  if (typeof error === 'string') return error;
  const data = error.response?.data;
  if (data && typeof data === 'object' && data.error != null) {
    const formatted = formatEnvelopeMessage(data.error);
    if (formatted != null && String(formatted).trim() !== '') {
      return String(formatted);
    }
  }
  if (data && typeof data === 'object' && typeof data.message === 'string') {
    const m = data.message;
    if (!looksLikeTechnicalLeak(m)) return m;
  }
  if (typeof data === 'string') {
    if (!looksLikeTechnicalLeak(data)) return data;
    return fallback;
  }
  const ax = error.message;
  if (typeof ax === 'string' && ax.startsWith('Request failed with status code')) {
    return fallback;
  }
  if (typeof ax === 'string' && ax && !looksLikeTechnicalLeak(ax)) return ax;
  return fallback;
}

const apiClient = axios.create({
  baseURL: getApiBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Backend exposes GET /datasets (grouped by type) only — no GET /datasets/:id.
 * @param {Record<string, Array<{ id?: string, name?: string, type?: string }>>} grouped
 * @param {string} datasetId
 * @returns {{ id: string, name: string, type: string } | null}
 */
export function findDatasetInGrouped(grouped, datasetId) {
  if (!grouped || datasetId === undefined || datasetId === null || datasetId === '') {
    return null;
  }
  for (const list of Object.values(grouped)) {
    if (!Array.isArray(list)) continue;
    const row = list.find(
      (d) => d && (d.id === datasetId || d.name === datasetId)
    );
    if (row) {
      return {
        id: row.id ?? row.name,
        name: row.name ?? row.id,
        type: row.type ?? '',
      };
    }
  }
  return null;
}

export const datasetService = {
  /**
   * @param {{ fullCatalog?: boolean }} [options]
   * Default list includes only studies with ingested clinical patient data.
   * Set fullCatalog true for operator catalog (matches `?full_catalog=1`).
   */
  getAllDatasets: async (options = {}) => {
    const params = {};
    if (options.fullCatalog) {
      params.full_catalog = '1';
    }
    const response = await apiClient.get('/datasets', { params });
    return response.data;
  },

  /**
   * Resolve study metadata: prefer ingested-only list, then full catalog (deep links).
   */
  getDatasetMeta: async (datasetId) => {
    let grouped = await datasetService.getAllDatasets({ fullCatalog: false });
    let meta = findDatasetInGrouped(grouped, datasetId);
    if (!meta) {
      grouped = await datasetService.getAllDatasets({ fullCatalog: true });
      meta = findDatasetInGrouped(grouped, datasetId);
    }
    return meta;
  },

  getClinicalData: async (datasetId, params = {}) => {
    const response = await apiClient.get(`/datasets/${datasetId}/clinical`, { params });
    return response.data;
  },

  getSummaryStats: async (datasetId) => {
    const response = await apiClient.get(`/datasets/${datasetId}/summary`);
    return response.data;
  },

  /** Ingested clinical table + on-disk matrix file flags (operators / UI hints). */
  getStudyDataStatus: async (datasetId) => {
    const { data } = await apiClient.get(`/datasets/${datasetId}/data-status`);
    return data;
  },

  runAnalysis: async (datasetId, params) => {
    const response = await apiClient.post(`/datasets/${datasetId}/analysis`, params);
    return response.data;
  },

  /**
   * Heatmap endpoint returns a Plotly figure (body may be a JSON string or object).
   * @returns {Promise<{ data: unknown, layout: unknown }>}
   */
  getHeatmapPlotly: async (datasetId) => {
    const { data } = await apiClient.get(`/datasets/${encodeURIComponent(datasetId)}/heatmap`);
    if (typeof data === 'string') {
      return JSON.parse(data);
    }
    return data;
  },
};

const RECENT_JOBS_KEY = 'bcancer_recent_jobs';
const RECENT_JOBS_MAX = 25;

export function readRecentJobIds() {
  try {
    const raw = sessionStorage.getItem(RECENT_JOBS_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function pushRecentJob(entry) {
  try {
    const prev = readRecentJobIds();
    const next = [
      {
        job_id: entry.job_id,
        study_id: entry.study_id,
        job_type: entry.job_type,
        saved_at: new Date().toISOString(),
      },
      ...prev.filter((e) => e.job_id !== entry.job_id),
    ].slice(0, RECENT_JOBS_MAX);
    sessionStorage.setItem(RECENT_JOBS_KEY, JSON.stringify(next));
  } catch {
    /* ignore quota */
  }
}

/**
 * Async Celery-backed analysis jobs (POST + poll status + result).
 */
/**
 * OpenAPI 3 document served by the API (currently includes async jobs paths).
 * @returns {Promise<Record<string, unknown>>}
 */
export async function fetchOpenApiSpec() {
  const { data } = await apiClient.get('/openapi.json');
  return data;
}

export const analysisJobService = {
  /**
   * @param {{ study_id: string, job_type?: string, parameters?: Record<string, unknown> }} body
   * @returns {Promise<{ job_id: string, status: string, study_id: string, job_type: string }>}
   */
  createJob: async (body) => {
    const response = await apiClient.post('/analysis/jobs', {
      study_id: body.study_id,
      job_type: body.job_type || 'generic',
      parameters: body.parameters || {},
    });
    return response.data;
  },

  /**
   * @returns {Promise<{ job_id: string, status: string, study_id: string, job_type: string, queued_at?: string, started_at?: string, finished_at?: string, error_message?: string }>}
   */
  getJob: async (jobId) => {
    const response = await apiClient.get(`/analysis/jobs/${jobId}`);
    return response.data;
  },

  /**
   * Result when completed. API returns 202 with api_error body until ready.
   * @returns {Promise<{ ready: true, data: { job_id: string, result: Record<string, unknown> } } | { ready: false, status: number, body: unknown }>}
   */
  getJobResult: async (jobId) => {
    const response = await apiClient.get(`/analysis/jobs/${jobId}/result`, {
      validateStatus: (status) => [200, 202, 404].includes(status),
    });
    if (response.status === 404) {
      const err = new Error('Job not found');
      err.response = response;
      throw err;
    }
    if (response.status === 202) {
      return { ready: false, status: 202, body: response.data };
    }
    return { ready: true, data: response.data };
  },
};

export { apiClient };
