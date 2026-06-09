import React, { useState } from "react";
import "../styles/OrgForm.css";

export type OrgFormValues = {
  org_name: string;
  region: string;
  api_base_url: string;
  client_id: string;
  client_secret: string;
};

type OrgFormProps = {
  values: OrgFormValues;
  onChange: (key: keyof OrgFormValues, value: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  onCancel?: () => void;
  submitLabel?: string;
  submitting?: boolean;
  disableOrgName?: boolean;
};

type Errors = Partial<Record<keyof OrgFormValues, string>>;

const OrgForm: React.FC<OrgFormProps> = ({
  values,
  onChange,
  onSubmit,
  onCancel,
  submitLabel = "Save",
  submitting = false,
  disableOrgName = false,
}) => {
  const [showSecret, setShowSecret] = useState(false);
  const [errors, setErrors] = useState<Errors>({});

  const validate = (): Errors => {
    const next: Errors = {};

    if (!values.org_name.trim()) next.org_name = "Organization Name is required.";
    if (!values.region.trim()) next.region = "Region is required.";
    if (!values.api_base_url.trim()) next.api_base_url = "API Base URL is required.";
    if (!values.client_id.trim()) next.client_id = "Client ID is required.";
    if (!values.client_secret.trim()) next.client_secret = "Client Secret is required.";

    // Optional URL format check
    if (values.api_base_url.trim()) {
      try {
        new URL(values.api_base_url.trim());
      } catch {
        next.api_base_url = "Please enter a valid URL (e.g. https://api.example.com).";
      }
    }

    return next;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const nextErrors = validate();
    setErrors(nextErrors);

    if (Object.keys(nextErrors).length > 0) return; // block submit

    onSubmit(e);
  };

  return (
    <form onSubmit={handleSubmit} className="card org-form-card border-0" noValidate>
      <div className="card-body p-4 p-md-5">
        <div className="row g-4">
          <Field
            id="org_name"
            label="Organization Name"
            icon="🏢"
            value={values.org_name}
            onChange={(v) => {
  onChange("org_name", v);
  setErrors((prev) => ({ ...prev, org_name: undefined }));
}}
            disabled={disableOrgName}
            required
            error={errors.org_name}
          />

          <Field
            id="region"
            label="Region"
            icon="🌍"
            value={values.region}
            onChange={(v) => {
  onChange("region", v);
  setErrors((prev) => ({ ...prev, region: undefined }));
}}
            required
            error={errors.region}
          />

          <Field
            id="api_base_url"
            label="API Base URL"
            icon="🔗"
            value={values.api_base_url}
            onChange={(v) => {
  onChange("api_base_url", v);
  setErrors((prev) => ({ ...prev, api_base_url: undefined }));
}}
            required
            error={errors.api_base_url}
          />

          <Field
            id="client_id"
            label="Client ID"
            icon="🆔"
            value={values.client_id}
            onChange={(v) => {
  onChange("client_id", v);
  setErrors((prev) => ({ ...prev, client_id: undefined }));
}}
            required
            error={errors.client_id}
          />

          <Field
            id="client_secret"
            label="Client Secret"
            icon="🔐"
            type={showSecret ? "text" : "password"}
            value={values.client_secret}
            onChange={(v) => {
  onChange("client_secret", v);
  setErrors((prev) => ({ ...prev, client_secret: undefined }));
}}
            required
            error={errors.client_secret}
            rightAction={
              <button
                type="button"
                className="secret-toggle-btn"
                onClick={() => setShowSecret((s) => !s)}
              >
                {showSecret ? "Hide" : "Show"}
              </button>
            }
          />
        </div>

        <div className="org-form-actions d-flex justify-content-end gap-3 mt-5">
          {onCancel && (
            <button
              type="button"
              className="btn btn-cancel-modern"
              onClick={onCancel}
              disabled={submitting}
            >
              Cancel
            </button>
          )}

          <button type="submit" className="btn btn-save-modern" disabled={submitting}>
            {submitting ? "Saving..." : submitLabel}
          </button>
        </div>
      </div>
    </form>
  );
};

type FieldProps = {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
  disabled?: boolean;
  icon?: string;
  rightAction?: React.ReactNode;
  required?: boolean;
  error?: string;
};

const Field: React.FC<FieldProps> = ({
  id,
  label,
  value,
  onChange,
  type = "text",
  disabled = false,
  icon = "•",
  rightAction,
  required = false,
  error,
}) => (
  <div className="col-12 col-md-6">
    <div className={`floating-group ${value ? "has-value" : ""} ${error ? "has-error" : ""}`}>
      <span className="field-icon" aria-hidden>
        {icon}
      </span>

      <input
        id={id}
        type={type}
        className={`form-control floating-input ${error ? "is-invalid" : ""}`}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        autoComplete="off"
        placeholder=" "
        required={required}
        aria-invalid={!!error}
        aria-describedby={error ? `${id}-error` : undefined}
      />

      <label htmlFor={id} className="floating-label">
        {label} {required ? "*" : ""}
      </label>

      {rightAction && <div className="field-right-action">{rightAction}</div>}
    </div>

    {error && (
      <div id={`${id}-error`} className="field-error-text">
        {error}
      </div>
    )}
  </div>
);

export default OrgForm;
