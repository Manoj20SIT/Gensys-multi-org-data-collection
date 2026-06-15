import React, { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import OrgForm, { type OrgFormValues } from "../components/OrgForm";
import { orgService } from "../services/orgService";
import "../styles/OrgView.css";

const AddOrg: React.FC = () => {
  const navigate = useNavigate();

  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [testResult, setTestResult] = useState<{
    type: "success" | "warning" | "error";
    message: string;
    missingAreas?: string[];
    permissionsRequired?: Record<string, string[]>;
  } | null>(null);

  const [form, setForm] = useState<OrgFormValues>({
    org_name: "",
    region: "",
    api_base_url: "",
    client_id: "",
    client_secret: "",
  });

  const initials = useMemo(
    () => (form.org_name || "N").slice(0, 1).toUpperCase(),
    [form.org_name]
  );

  // ✅ Enable Test Connection only when all fields are filled
  const canTestConnection = Boolean(
    form.org_name.trim() &&
    form.region.trim() &&
    form.api_base_url.trim() &&
    form.client_id.trim() &&
    form.client_secret.trim()
  );

  const handleChange = (key: keyof OrgFormValues, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }));
    if (error) setError("");
    if (testResult) setTestResult(null); // clear stale test result on edits
  };

  const handleTestConnection = async () => {
    setError("");
    setSuccess("");
    setTestResult(null);

    setTesting(true);
    try {
      const payload = {
        org_name: form.org_name.trim(),
        region: form.region.trim(),
        api_base_url: form.api_base_url.trim(),
        client_id: form.client_id.trim(),
        client_secret: form.client_secret.trim(),
      };

      const data = await orgService.testConnection(payload);
      console.log("the new connection object received is ", data)

      if (data?.success) {
        setTestResult({
          type: "success",
          message: "Connection successful. All required permissions are available.",
        });
      } else {
        const first = data?.results?.[0] || {};
        setTestResult({
          type: "warning",
          message: data?.message || first?.message || "Permission issues found",
          missingAreas: first?.missingAreas || [],
          permissionsRequired: first?.permissions_required || {},
        });
      }
    } catch (e: any) {
      const detail = e?.response?.data?.detail;
      const msg =
        (typeof detail === "string" ? detail : detail?.message) ||
        e?.message ||
        "Connection test failed.";
      setTestResult({
        type: "error",
        message: msg,
      });
    } finally {
      setTesting(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    setSaving(true);
    try {
      const payload = {
        org_name: form.org_name.trim(),
        region: form.region.trim(),
        api_base_url: form.api_base_url.trim(),
        client_id: form.client_id.trim(),
        client_secret: form.client_secret.trim(),
      };

      await orgService.createOrg(payload as any);

      setSuccess("Organization created successfully.");
      navigate(`/orgs/${encodeURIComponent(form.org_name.trim())}`);
    } catch (e: any) {
      setError(
        e?.response?.data?.detail || e?.message || "Failed to create organization"
      );
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="container py-4 py-md-5">
      {/* Hero */}
      <div className="home-hero p-4 p-md-5 mb-4">
        <div className="d-flex justify-content-between align-items-start flex-wrap gap-3">
          <div>
            <p className="hero-kicker text-uppercase mb-2 small">Create Organization</p>
            <h2 className="mb-2 fw-bold">{form.org_name || "New Organization"}</h2>
            <p className="hero-subtitle mb-0">
              Add a new org and configure its connection details.
            </p>
          </div>
          <div className="org-avatar">{initials}</div>
        </div>
      </div>

      {/* top actions */}
      <div className="d-flex gap-2 mb-4">
        <button className="btn btn-outline-dark" onClick={() => navigate(-1)}>
          ← Back
        </button>

        <button
          type="button"
          className="btn btn-primary"
          onClick={handleTestConnection}
          disabled={!canTestConnection || testing || saving}
        >
          {testing ? "Testing..." : "Test Connection"}
        </button>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {testResult && (
  <div className={`conn-report conn-report--${testResult.type}`} role="alert">
    <button
      type="button"
      className="conn-report__close"
      aria-label="Close report"
      onClick={() => setTestResult(null)}
      title="Close"
    >
      ×
    </button>

    <div className="conn-report__header">
      <div className="conn-report__title">
        {testResult.type === "success"
          ? "Connection Successful"
          : testResult.type === "warning"
          ? "Permission Issues Found"
          : "Connection Failed"}
      </div>
      <div className="conn-report__msg">{testResult.message}</div>
    </div>

    {testResult.type === "warning" && (
      <div className="conn-report__body">
        {!!testResult.missingAreas?.length && (
          <div className="mb-2">
            <div className="fw-semibold mb-1">Missing Areas</div>
            <div className="d-flex flex-wrap gap-2">
              {testResult.missingAreas.map((a) => (
                <span key={a} className="conn-chip">{a}</span>
              ))}
            </div>
          </div>
        )}

        {!!Object.keys(testResult.permissionsRequired || {}).length && (
          <div>
            <div className="fw-semibold mb-1">Required Permissions</div>
            <div className="conn-perm-grid">
              {Object.entries(testResult.permissionsRequired || {}).map(([area, perms]) => (
                <div key={area} className="conn-perm-item">
                  <div className="conn-perm-area">{area}</div>
                  <div className="conn-perm-list">{perms.join(", ")}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    )}
  </div>
)}



      <OrgForm
        values={form}
        onChange={handleChange}
        onSubmit={handleSubmit}
        onCancel={() => navigate(-1)}
        submitLabel="Create Organization"
        submitting={saving}
      />
    </div>
  );
};

export default AddOrg;
