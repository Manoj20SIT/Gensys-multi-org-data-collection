import React, { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { orgService, type Org } from "../services/orgService";
import OrgForm, { type OrgFormValues } from "../components/OrgForm";
import "../styles/OrgForm.css";

const EditOrg: React.FC = () => {
  const { orgName } = useParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [originalName, setOriginalName] = useState("");

  const [form, setForm] = useState<OrgFormValues>({
    org_name: "",
    region: "",
    api_base_url: "",
    client_id: "",
    client_secret: "",
  });

  useEffect(() => {
    const load = async () => {
      if (!orgName) {
        setError("Organization name missing in URL");
        setLoading(false);
        return;
      }

      setLoading(true);
      setError("");
      setSuccess("");

      try {
        const data: Org = await orgService.getOrgByName(decodeURIComponent(orgName));
        setOriginalName(data.org_name || "");
        setForm({
          org_name: data.org_name || "",
          region: data.connection?.region || "",
          api_base_url: data.connection?.api_base_url || "",
          client_id: data.connection?.client_id || "",
          client_secret: data.connection?.client_secret || "",
        });
      } catch (e: any) {
        setError(e?.response?.data?.detail || e?.message || "Failed to load organization");
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [orgName]);

  const initials = useMemo(
    () => (form.org_name || "O").slice(0, 1).toUpperCase(),
    [form.org_name]
  );

  const handleChange = (key: keyof OrgFormValues, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    setSuccess("");

    try {
      const payload = {
        org_name: form.org_name.trim(),
        connection: {
          region: form.region.trim(),
          api_base_url: form.api_base_url.trim(),
          client_id: form.client_id.trim(),
          client_secret: form.client_secret.trim(),
        },
      };

      await orgService.updateOrg(originalName, payload as any);
      setSuccess("Organization updated successfully.");

      if (originalName !== form.org_name.trim()) {
        const newName = form.org_name.trim();
        setOriginalName(newName);
        navigate(`/orgs/${encodeURIComponent(newName)}/edit`, { replace: true });
      }
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || "Failed to save organization");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="container py-4 py-md-5">
      {/* Hero with same theme */}
      <div className="home-hero p-4 p-md-5 mb-4">
        <div className="d-flex justify-content-between align-items-start flex-wrap gap-3">
          <div>
            <p className="hero-kicker text-uppercase mb-2 small">Edit Organization</p>
            <h2 className="mb-2 fw-bold">{form.org_name || "Organization"}</h2>
            <p className="hero-subtitle mb-0">Update details and save changes.</p>
          </div>
          <div className="org-avatar">{initials}</div>
        </div>
      </div>

      <div className="d-flex gap-2 mb-4">
        <button className="btn btn-outline-dark" onClick={() => navigate(-1)}>
          ← Back
        </button>
      </div>

      {loading && <div className="card empty-card border-0 shadow-sm p-4">Loading...</div>}
      {error && <div className="alert alert-danger">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      {!loading && (
        <OrgForm
          values={form}
          onChange={handleChange}
          onSubmit={handleSubmit}
          onCancel={() => navigate(-1)}
          submitLabel="Save Changes"
          submitting={saving}
        />
      )}
    </div>
  );
};

export default EditOrg;
