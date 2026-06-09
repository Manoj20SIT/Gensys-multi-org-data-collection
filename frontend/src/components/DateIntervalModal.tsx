import React, { useEffect, useMemo, useState } from "react";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import "../styles/DateIntervalModal.css";

type Props = {
  show: boolean;
  loading?: boolean;
  title?: string;
  onClose: () => void;
  onSubmit: (interval: string) => Promise<void> | void;
};

const DateIntervalModal: React.FC<Props> = ({
  show,
  loading = false,
  title = "Run Collection",
  onClose,
  onSubmit,
}) => {
  const [fromDate, setFromDate] = useState<Date | null>(null);
  const [toDate, setToDate] = useState<Date | null>(null);
  const [localError, setLocalError] = useState("");

  useEffect(() => {
    if (!show) return;
    const now = new Date();
    const from = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    setFromDate(from);
    setToDate(now);
    setLocalError("");
  }, [show]);

  const previewInterval = useMemo(() => {
    if (!fromDate || !toDate) return "";
    return `${fromDate.toISOString()}/${toDate.toISOString()}`;
  }, [fromDate, toDate]);

  if (!show) return null;

  const setPreset = (hours: number) => {
    const now = new Date();
    const from = new Date(now.getTime() - hours * 60 * 60 * 1000);
    setFromDate(from);
    setToDate(now);
    setLocalError("");
  };

  const handleSubmit = async () => {
    setLocalError("");

    if (!fromDate || !toDate) {
      setLocalError("Please select both From and To date/time.");
      return;
    }

    if (fromDate >= toDate) {
      setLocalError("From date/time must be earlier than To date/time.");
      return;
    }

    await onSubmit(`${fromDate.toISOString()}/${toDate.toISOString()}`);
  };

  return (
    <div className="rcm-overlay" role="dialog" aria-modal="true">
      <div className="rcm-modal">
        {/* Header */}
        <div className="rcm-header">
          <div>
            <h4 className="rcm-title">{title}</h4>
            <p className="rcm-subtitle">Choose date/time range to generate metrics</p>
          </div>
          <button className="rcm-close" onClick={onClose} disabled={loading} aria-label="Close">
            ✕
          </button>
        </div>

        {/* Error */}
        {localError && <div className="rcm-error">{localError}</div>}

        {/* Presets */}
        <div className="rcm-presets">
          <button type="button" className="rcm-chip" onClick={() => setPreset(1)} disabled={loading}>
            Last 1 hour
          </button>
          <button type="button" className="rcm-chip" onClick={() => setPreset(24)} disabled={loading}>
            Last 24 hours
          </button>
          <button type="button" className="rcm-chip" onClick={() => setPreset(24 * 7)} disabled={loading}>
            Last 7 days
          </button>
        </div>

        {/* Pickers */}
        <div className="rcm-grid">
          <div className="rcm-field">
            <label>From</label>
            <DatePicker
              selected={fromDate}
              onChange={(date: Date | null) => setFromDate(date)}
              showTimeSelect
              timeIntervals={15}
              dateFormat="MMM dd, yyyy h:mm aa"
              className="rcm-input"
              placeholderText="Select from date & time"
              disabled={loading}
              maxDate={toDate || undefined}
              popperClassName="rcm-datepicker-popper"
              calendarClassName="rcm-datepicker"
            />
          </div>

          <div className="rcm-field">
            <label>To</label>
            <DatePicker
              selected={toDate}
              onChange={(date: Date | null) => setToDate(date)}
              showTimeSelect
              timeIntervals={15}
              dateFormat="MMM dd, yyyy h:mm aa"
              className="rcm-input"
              placeholderText="Select to date & time"
              disabled={loading}
              minDate={fromDate || undefined}
              popperClassName="rcm-datepicker-popper"
              calendarClassName="rcm-datepicker"
            />
          </div>
        </div>

        {/* Preview */}
        <div className="rcm-preview">
          <div className="rcm-preview-label">Interval Preview (UTC)</div>
          <code>{previewInterval || "Select valid date/time range"}</code>
        </div>

        {/* Footer */}
        <div className="rcm-footer">
          <button className="rcm-btn rcm-btn-secondary" onClick={onClose} disabled={loading}>
            Cancel
          </button>
          <button className="rcm-btn rcm-btn-primary" onClick={handleSubmit} disabled={loading}>
            {loading ? (
              <>
                <span className="rcm-spinner" />
                Generating...
              </>
            ) : (
              "Run Now"
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default DateIntervalModal;
