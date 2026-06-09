import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { orgService } from "../services/orgService";
import { collectionService } from "../services/collectionService";
// import RunCollectionModal from "../components/RunCollectionModal";
import "../styles/home.css";
import DateIntervalModal from "../components/DateIntervalModal";
import type { RunCollectionResponse } from "../types/RunCollectionTypes";
import type { Org } from "../types/OrgTypes";

const Home: React.FC = () => {
  const [orgs, setOrgs] = useState<Org[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [showRunModal, setShowRunModal] = useState(false);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const navigate = useNavigate();
  const loadOrgs = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await orgService.getOrgs();
      setOrgs(data.orgs ?? []);
      setTotal(data.total_orgs ?? 0);
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || "Failed to fetch organizations");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOrgs();
  }, []);

  const filteredOrgs = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return orgs;
    return orgs.filter((o) => o.org_name?.toLowerCase().includes(q));
  }, [orgs, query]);

  const onRunClick = () => {
    setError("");
    setShowRunModal(true);
  };

  const handleRunSubmit = async (interval: string) => {
    try {
      setRunning(true);
      setError("");

      const runResponse: RunCollectionResponse = await collectionService.runCollection({
        interval,
        fields: [],
      });

      setShowRunModal(false);
      navigate("/run-results", { state: { runResponse } });
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || "Failed to run collection");
    } finally {
      setRunning(false);
    }
  };

  const onView = (orgName: string) => {
    const path = `/orgs/${encodeURIComponent(orgName)}`;
    navigate(path);
    console.log("onView clicked", { orgName, path });
  };

  const onEdit = (orgName: string) => navigate(`/orgs/${encodeURIComponent(orgName)}/edit`);

  const onDelete = async (orgName: string) => {
    const ok = window.confirm(`Delete org "${orgName}"?`);
    if (!ok) return;
    try {
      await orgService.deleteOrg(orgName);
      await loadOrgs();
    } catch (e: any) {
      alert(e?.response?.data?.detail || "Failed to delete org");
    }
  };

  return (
    <div className="container py-4">
      {/* HERO */}
      <div className="home-hero p-4 p-md-5 mb-4">
        <div className="d-flex flex-wrap justify-content-between align-items-center gap-3">
          <div>
            <div className="text-uppercase small fw-semibold hero-kicker mb-2">Dashboard</div>
            <h2 className="mb-1 fw-bold">Genesys Organizations</h2>
            <p className="mb-0 hero-subtitle">View, edit, and manage your configured orgs.</p>
          </div>

          <div className="d-flex align-items-center gap-2 flex-wrap">
            <span className="badge rounded-pill stat-pill px-3 py-2">Total: {total}</span>

            <button className="btn btn-light fw-semibold px-3" onClick={() => navigate("/orgs/add")}>
              + Add Org
            </button>

            <button
              className="btn btn-primary fw-semibold px-3 d-flex align-items-center gap-2"
              onClick={onRunClick}
              disabled={running}
              title="Run collection for all orgs"
            >
              {running ? (
                <>
                  <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true" />
                  Generating...
                </>
              ) : (
                <>▶ Run</>
              )}
            </button>

            <button className="btn btn-warning fw-semibold px-3" onClick={loadOrgs} disabled={loading}>
              {loading ? "Refreshing..." : "Refresh"}
            </button>
          </div>
        </div>

        <div className="mt-3">
          <input
            type="text"
            className="form-control form-control-lg shadow-sm"
            placeholder="Search organization by name..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
      </div>

      {error && <div className="alert alert-danger shadow-sm">{error}</div>}

      {loading ? (
        <div className="text-center py-5">
          <div className="spinner-border text-warning" role="status" />
          <p className="mt-3 text-muted mb-0">Loading organizations...</p>
        </div>
      ) : filteredOrgs.length === 0 ? (
        <div className="card empty-card border-0 shadow-sm">
          <div className="card-body text-center py-5">
            <h5 className="mb-2">No matching organizations</h5>
            <p className="text-muted mb-0">Try a different search or refresh.</p>
          </div>
        </div>
      ) : (
        <div className="d-grid gap-3">
          {filteredOrgs.map((org) => (
            <div key={org.org_name} className="org-row card  shadow-sm">
              <div className="card-body org-row-body d-flex flex-wrap justify-content-between align-items-center gap-3">
                <div className="d-flex align-items-center gap-3">
                  <div className="org-avatar">{org.org_name?.charAt(0)?.toUpperCase() || "O"}</div>
                  <div className="org-name-wrap  always-visible" >
                    <h5 className="mb-0 fw-bold org-name">{org.org_name}</h5>
                    <small className=" org-meta">Organization</small>
                  </div>
                </div>

                <div className="d-flex gap-2">
                  <button className="btn btn-outline-dark rounded-pill px-3" onClick={() => onView(org.org_name)}>
                    View
                  </button>
                  <button className="btn btn-outline-warning rounded-pill px-3" onClick={() => onEdit(org.org_name)}>
                    Edit
                  </button>
                  <button className="btn btn-outline-danger rounded-pill px-3" onClick={() => onDelete(org.org_name)}>
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Reusable Run Modal */}
      <DateIntervalModal
        show={showRunModal}
        loading={running}
        title="Run Collection"
        onClose={() => !running && setShowRunModal(false)}
        onSubmit={handleRunSubmit}
      />
    </div>
  );
};

export default Home;
