import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { orgService} from "../services/orgService";
import "../styles/OrgView.css";
import type { Org } from "../types/OrgTypes";

const OrgView: React.FC = () => {
  const { orgName } = useParams();
  const navigate = useNavigate();

  const [org, setOrg] = useState<Org | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchOrg = async () => {
      if (!orgName) {
        setError("Organization name missing in URL");
        setLoading(false);
        return;
      }

      setLoading(true);
      setError("");

      try {
        const data = await orgService.getOrgByName(decodeURIComponent(orgName));
        setOrg(data);
      } catch (e: any) {
        setError(e?.response?.data?.detail || e?.message || "Failed to load organization");
      } finally {
        setLoading(false);
      }
    };

    fetchOrg();
  }, [orgName]);

  const connection = org?.connection ?? {};
  const initials = (org?.org_name || "O").slice(0, 1).toUpperCase();

  return (
    <div className="container py-4 py-md-5">
      {/* Header / Hero */}
      <div className="home-hero p-4 p-md-5 mb-4">
        <div className="d-flex justify-content-between align-items-start flex-wrap gap-3">
          <div>
            <p className="hero-kicker text-uppercase mb-2 small">Organization Details</p>
            <h2 className="mb-2 fw-bold">{org?.org_name ?? "Organization"}</h2>
            <p className="hero-subtitle mb-0">
              View connection details and credentials configuration.
            </p>
          </div>

          <div className="org-avatar">{initials}</div>
        </div>
      </div>

      {/* Actions */}
      <div className="d-flex gap-2 mb-4">
        <button className="btn btn-outline-dark" onClick={() => navigate("/")}>
          ← Back
        </button>
        <button
          className="btn btn-warning fw-semibold"
          onClick={() => navigate(`/orgs/${encodeURIComponent(org?.org_name || "")}/edit`)}
          disabled={!org}
        >
          Edit Org
        </button>
      </div>

      {loading && <div className="card empty-card border-0 shadow-sm p-4">Loading...</div>}
      {error && <div className="alert alert-danger">{error}</div>}

      {!loading && org && (
        <div className="card org-row border-0 shadow-sm">
          <div className="card-body p-4 p-md-5">
            <div className="row g-3">
              <Info label="Region" value={connection.region ?? "-"} />
              <Info label="API Base URL" value={connection.api_base_url ?? "-"} mono />
              <Info label="Client ID" value={connection.client_id ?? "-"} mono />
              <Info label="Client Secret" value={connection.client_secret ?? "-"} mono />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const Info: React.FC<{ label: string; value: string; mono?: boolean }> = ({ label, value, mono }) => (
  <div className="col-12 col-md-6">
    <div className="stat-pill p-3 rounded-3 h-100 info-dark-pill">
      <div className="small text-uppercase opacity-75 mb-1">{label}</div>
      <div className={`fw-semibold ${mono ? "font-monospace" : ""}`}>{value}</div>
    </div>
  </div>
);

export default OrgView;
