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

  return (
    <form onSubmit={onSubmit} className="card org-form-card border-0">
      <div className="card-body p-4 p-md-5">
        <div className="row g-4">
          <Field
            id="org_name"
            label="Organization Name"
            icon="🏢"
            value={values.org_name}
            onChange={(v) => onChange("org_name", v)}
            disabled={disableOrgName}
          />

          <Field
            id="region"
            label="Region"
            icon="🌍"
            value={values.region}
            onChange={(v) => onChange("region", v)}
          />

          <Field
            id="api_base_url"
            label="API Base URL"
            icon="🔗"
            value={values.api_base_url}
            onChange={(v) => onChange("api_base_url", v)}
          />

          <Field
            id="client_id"
            label="Client ID"
            icon="🆔"
            value={values.client_id}
            onChange={(v) => onChange("client_id", v)}
          />

          <Field
            id="client_secret"
            label="Client Secret"
            icon="🔐"
            type={showSecret ? "text" : "password"}
            value={values.client_secret}
            onChange={(v) => onChange("client_secret", v)}
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
}) => (
  <div className="col-12 col-md-6">
    <div className={`floating-group ${value ? "has-value" : ""}`}>
      <span className="field-icon" aria-hidden>
        {icon}
      </span>

      <input
        id={id}
        type={type}
        className="form-control floating-input"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        autoComplete="off"
        placeholder=" "
      />

      <label htmlFor={id} className="floating-label">
        {label}
      </label>

      {rightAction && <div className="field-right-action">{rightAction}</div>}
    </div>
  </div>
);

export default OrgForm;
