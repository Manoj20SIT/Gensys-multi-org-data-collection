import React, { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import OrgForm, { type OrgFormValues } from "../components/OrgForm";
import { orgService } from "../services/orgService";
import "../styles/OrgView.css"; // reusing same themed classes

const AddOrg: React.FC = () => {
  const navigate = useNavigate();

  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

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

  const handleChange = (key: keyof OrgFormValues, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }));
    if (error) setError("");
  };

  // const validate = () => {
  //   if (!form.org_name.trim()) return "Organization Name is required";
  //   if (!form.region.trim()) return "Region is required";
  //   if (!form.api_base_url.trim()) return "API Base URL is required";
  //   if (!form.client_id.trim()) return "Client ID is required";
  //   if (!form.client_secret.trim()) return "Client Secret is required";
  //   return "";
  // };

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
    setError(e?.response?.data?.detail || e?.message || "Failed to create organization");
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
      </div>

      {error && <div className="alert alert-danger">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

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
