// src/components/ClinicalData/ClinicalData.js
import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { datasetService, getErrorMessage } from '../../services/api';
import { formatFieldLabel } from '../../utils/helpers';
import './ClinicalData.css';

const PAGE_SIZE_OPTIONS = [10, 25, 50, 100, 200, 500];

const ClinicalData = ({ datasetId }) => {
  const [rows, setRows] = useState([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [pageSize, setPageSize] = useState(25);
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({});

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setLoading(true);
      setError(null);
      const off = (currentPage - 1) * pageSize;
      try {
        const data = await datasetService.getClinicalData(datasetId, {
          limit: pageSize,
          offset: off,
        });
        if (cancelled) return;
        const items = Array.isArray(data) ? data : data.items ?? [];
        setRows(items);
        setTotal(typeof data.total === 'number' ? data.total : items.length);
        setOffset(typeof data.offset === 'number' ? data.offset : off);
      } catch (e) {
        if (!cancelled) {
          setError(getErrorMessage(e, 'Failed to fetch clinical data'));
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, [datasetId, currentPage, pageSize]);

  useEffect(() => {
    setCurrentPage(1);
    setFilters({});
  }, [datasetId, pageSize]);

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  useEffect(() => {
    if (currentPage > totalPages) {
      setCurrentPage(totalPages);
    }
  }, [totalPages, currentPage]);

  const filteredRows = useMemo(() => {
    if (rows.length === 0) return [];
    let result = [...rows];
    Object.entries(filters).forEach(([field, value]) => {
      if (!value) return;
      result = result.filter((item) => {
        const v = item[field];
        if (typeof v === 'string') {
          return v.toLowerCase().includes(String(value).toLowerCase());
        }
        if (typeof v === 'number' && !Number.isNaN(v)) {
          return v === Number(value);
        }
        return String(v) === String(value);
      });
    });
    return result;
  }, [rows, filters]);

  const hasActiveFilters = useMemo(
    () => Object.values(filters).some((v) => v && String(v).trim() !== ''),
    [filters]
  );

  const handleFilterChange = useCallback((field, value) => {
    setFilters((prev) => ({
      ...prev,
      [field]: value,
    }));
  }, []);

  const resetFilters = useCallback(() => {
    setFilters({});
  }, []);

  const handlePageSizeChange = (e) => {
    setPageSize(Number(e.target.value));
  };

  const paginate = (pageNumber) => {
    setCurrentPage(Math.min(Math.max(1, pageNumber), totalPages));
  };

  if (loading) return <div className="loading">Loading clinical data...</div>;
  if (error) return <div className="error">{error}</div>;
  if (total === 0 && !loading) {
    return <div className="warning">No clinical data available for this study.</div>;
  }

  const fixedHeaders = [
    'Patient ID',
    'Age',
    'Gender',
    'Race',
    'Survival (months)',
    'Tumor Stage',
    'Status',
  ];

  const fieldMapping = {
    'Patient ID': 'patient_id',
    Age: 'age',
    Gender: 'gender',
    Race: 'race',
    'Tumor Stage': 'stage',
    'Survival (months)': 'survival_months',
    Status: 'status',
  };

  const filterFields = Object.values(fieldMapping).filter(
    (field) => field !== 'patient_id' && field !== 'sample_id'
  );

  const rangeStart = total === 0 ? 0 : offset + 1;
  const rangeEnd = offset + rows.length;

  return (
    <div className="clinical-data-container">
      <h2>Clinical Data</h2>

      <p className="clinical-meta">
        Showing <strong>{rangeStart}</strong>–<strong>{rangeEnd}</strong> of{' '}
        <strong>{total}</strong> patients (page {currentPage} of {totalPages}, up to{' '}
        {pageSize} per request).
      </p>

      {hasActiveFilters && (
        <p className="clinical-filter-note">
          Text filters apply only to the rows loaded on this page. Clear filters and use
          pagination to scan other pages.
        </p>
      )}

      <div className="table-filters">
        {filterFields.map((field) => (
          <div key={field} className="filter-group">
            <label className="filter-label" htmlFor={`filter-${field}`}>
              {formatFieldLabel(field)}
            </label>
            <input
              id={`filter-${field}`}
              type="text"
              className="filter-input"
              value={filters[field] || ''}
              onChange={(e) => handleFilterChange(field, e.target.value)}
              placeholder={`Filter by ${formatFieldLabel(field)}`}
            />
          </div>
        ))}

        <button type="button" className="reset-filters" onClick={resetFilters}>
          Reset Filters
        </button>
      </div>

      <div className="table-responsive">
        <table className="clinical-table">
          <thead>
            <tr>
              {fixedHeaders.map((header) => (
                <th key={header}>{header}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filteredRows.length > 0 ? (
              filteredRows.map((patient, index) => (
                <tr key={`${patient.patient_id ?? patient.sample_id ?? 'row'}-${index}`}>
                  {fixedHeaders.map((header) => {
                    const field = fieldMapping[header];
                    return (
                      <td key={field}>
                        {header === 'Status' ? (
                          <span
                            className={`status-badge ${
                              patient[field] === 'Alive'
                                ? 'status-alive'
                                : 'status-deceased'
                            }`}
                          >
                            {patient[field]}
                          </span>
                        ) : (
                          patient[field]
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={fixedHeaders.length} className="no-data">
                  No matching rows on this page (try clearing filters or another page).
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="pagination">
        <div className="pagination-info">
          {hasActiveFilters
            ? `Filtered view: ${filteredRows.length} row(s) on this page.`
            : `Page ${currentPage} of ${totalPages}`}
        </div>

        <div className="items-per-page">
          <label htmlFor="clinical-page-size">
            Rows per page
            <select
              id="clinical-page-size"
              value={pageSize}
              onChange={handlePageSizeChange}
              className="filter-input"
            >
              {PAGE_SIZE_OPTIONS.map((n) => (
                <option key={n} value={n}>
                  {n}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="pagination-controls">
          <button
            type="button"
            className="pagination-button"
            onClick={() => paginate(1)}
            disabled={currentPage === 1}
          >
            First
          </button>
          <button
            type="button"
            className="pagination-button"
            onClick={() => paginate(currentPage - 1)}
            disabled={currentPage === 1}
          >
            Prev
          </button>

          {[...Array(Math.min(totalPages, 5)).keys()].map((i) => {
            let pageNum;
            if (totalPages <= 5) {
              pageNum = i + 1;
            } else if (currentPage <= 3) {
              pageNum = i + 1;
            } else if (currentPage >= totalPages - 2) {
              pageNum = totalPages - 4 + i;
            } else {
              pageNum = currentPage - 2 + i;
            }

            return (
              <button
                type="button"
                key={pageNum}
                className={`pagination-button ${currentPage === pageNum ? 'active' : ''}`}
                onClick={() => paginate(pageNum)}
              >
                {pageNum}
              </button>
            );
          })}

          <button
            type="button"
            className="pagination-button"
            onClick={() => paginate(currentPage + 1)}
            disabled={currentPage === totalPages}
          >
            Next
          </button>
          <button
            type="button"
            className="pagination-button"
            onClick={() => paginate(totalPages)}
            disabled={currentPage === totalPages}
          >
            Last
          </button>
        </div>
      </div>
    </div>
  );
};

export default ClinicalData;
