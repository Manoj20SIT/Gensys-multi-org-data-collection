import React, { useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
// import type { RunCollectionResponse } from "../services/collectionService";
 import authService from "../services/authService";
import "../styles/runResults.css";
import type { RunCollectionResponse } from "../types/RunCollectionTypes";

const prettyKey = (k: string) =>
  k.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

const formatValue = (v: any, key?: string) => {
  if (v === null || v === undefined) return "-";
  if (typeof v === "boolean") return v ? "Yes" : "No";

  const normalizedKey = (key || "").toLowerCase().replace(/[_\s]/g, "");

  // matches: seatAdoptionBucket, seat_adoption_bucket, role_head_seat_adoption_bucket, etc.
  if (normalizedKey.includes("seatadoptionbucket")) {
    const n = Number(v);
    if (Number.isNaN(n)) return String(v); // if already like "80%", keep as text
    return `${n.toFixed(2)}%`;
  }
  

  if (typeof v === "number") return Number.isInteger(v) ? v.toString() : v.toFixed(2);
  if (typeof v === "object") return JSON.stringify(v);
  return String(v);
};


const getValueClass = (v: any) => {
  if (typeof v === "number") return v > 0 ? "rr-val rr-val-num" : "rr-val rr-val-zero";
  if (typeof v === "string") {
    const s = v.toLowerCase();
    if (["active", "enabled"].includes(s)) return "rr-val rr-val-good";
    if (["inactive", "disabled", "unknown"].includes(s)) return "rr-val rr-val-muted";
  }
  return "rr-val";
};

const RunResults: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const runResponse = location.state?.runResponse as RunCollectionResponse | undefined;

  const [search, setSearch] = useState("");

  const results = runResponse?.results ?? [];

  const filteredResults = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return results;
    return results.filter((r) => r.org_name?.toLowerCase().includes(q));
  }, [results, search]);

  const metricColumns = useMemo(() => {
    const set = new Set<string>();
    results.forEach((r) => {
      if (r.metrics && typeof r.metrics === "object") {
        Object.keys(r.metrics).forEach((k) => set.add(k));
      }
    });
    return Array.from(set);
  }, [results]);

  const handleDownload = () => {
    if (!runResponse?.download_url) return;
    const baseURL = authService.api.defaults.baseURL || "";
    window.open(`${baseURL}${runResponse.download_url}`, "_blank");
  };

  if (!runResponse) {
    return (
      <div className="rr-page">
        <div className="rr-empty">
          <h3>No run response found</h3>
          <p>Please run collection first.</p>
          <button className="rr-btn rr-btn-primary" onClick={() => navigate("/")}>
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  return (
  <div className="rr-page">
    <div className="rr-container">

      {/* Top unified panel */}
      <section className="rr-top-panel">
        <div className="rr-header-row">
          <div>
            <h2 className="rr-title">Collection Run Results</h2>
            <p className="rr-subtitle">
              Understand organization metrics quickly in a clean tabular view.
            </p>
          </div>

          <div className="rr-actions">
            <button className="rr-btn rr-btn-ghost" onClick={() => navigate("/")}>
              Back Home
            </button>
            <button
              className="rr-btn rr-btn-success"
              onClick={handleDownload}
              disabled={!runResponse.download_url}
              title={runResponse.file_name || "Excel not available"}
            >
              Download Excel
            </button>
          </div>
        </div>

        <div className="rr-kpi-grid">
          <div className="rr-kpi-card">
            <span>Total Orgs</span>
            <strong>{runResponse.total_orgs ?? 0}</strong>
          </div>
          <div className="rr-kpi-card">
            <span>Processed</span>
            <strong>{results.length}</strong>
          </div>
          <div className="rr-kpi-card">
            <span>Metrics Columns</span>
            <strong>{metricColumns.length}</strong>
          </div>
          <div className="rr-kpi-card">
            <span>Requested Fields</span>
            <strong>{runResponse.requested_fields?.length || 0}</strong>
          </div>
        </div>

        <div className="rr-meta-chips">
          <div className="rr-chip"><b>Mode:</b> {runResponse.mode || "-"}</div>
          <div className="rr-chip">
            <b>Requested:</b>{" "}
            {runResponse.requested_fields?.length
              ? runResponse.requested_fields.join(", ")
              : "All/default"}
          </div>
          <div className="rr-chip"><b>File:</b> {runResponse.file_name || "-"}</div>
        </div>
      </section>

      {/* Tools */}
      <div className="rr-toolbar">
        <input
          className="rr-search"
          placeholder="Search organization..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <div className="rr-count-pill">{filteredResults.length} row(s)</div>
      </div>

      {/* Table */}
      <div className="rr-grid-wrap">
        {filteredResults.length === 0 ? (
          <div className="rr-no-data">No matching organization found.</div>
        ) : (
          <table className="rr-grid">
            <thead>
              <tr>
                <th className="sticky idx">#</th>
                <th className="sticky org">Organization</th>
                {metricColumns.map((col) => (
                  <th key={col}>{prettyKey(col)}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filteredResults.map((r, idx) => (
                <tr key={`${r.org_name}-${idx}`}>
                  <td className="sticky idx">{idx + 1}</td>
                  <td className="sticky org">{r.org_name}</td>
                  {metricColumns.map((col) => {
                    const val = r.metrics?.[col];
                    return (
                      <td key={col}>
                        <span className={getValueClass(val)}>{formatValue(val,col)}</span>
                        
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  </div>
);

};

export default RunResults;
