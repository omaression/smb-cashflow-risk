"use client";

import { useState, useCallback } from "react";
import Link from "next/link";

type Step = "upload" | "mapping" | "validation" | "import";

interface FileStatus {
  name: string;
  size: number;
  status: "pending" | "uploading" | "uploaded" | "error";
  error?: string;
}

interface MappingField {
  canonical_field: string;
  source_field: string | null;
  confidence: number;
  required: boolean;
  resolved: boolean;
  alternatives: string[];
}

interface FilePreview {
  filename: string;
  detected_role: string | null;
  detection_confidence: number | null;
  row_count: number;
  headers: string[];
  detection_reasons: string[];
  parse_warnings: string[];
  suggested_mapping: Record<string, Record<string, unknown>>;
  alternative_roles: Array<{ role: string; confidence: number }>;
  required_missing: string[];
  ambiguity_warnings: string[];
}

interface QualityProfile {
  completeness_score: number | null;
  consistency_score: number | null;
  coverage_score: number | null;
  history_depth_score: number | null;
  sample_size_score: number | null;
  overall_confidence_score: number | null;
  reliability_grade: string | null;
  recommendations: string[];
}

interface ImportPreviewResponse {
  workspace_id: string;
  status: string;
  source_file_count: number;
  files: FilePreview[];
  quality_profile: QualityProfile;
}

export default function TryPage() {
  const [step, setStep] = useState<Step>("upload");
  const [files, setFiles] = useState<FileStatus[]>([]);
  const [preview, setPreview] = useState<ImportPreviewResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    if (!event.target.files) return;
    const selected = Array.from(event.target.files).map((file) => ({
      name: file.name,
      size: file.size,
      status: "pending" as const,
    }));
    setFiles(selected);
    setError(null);
  }, []);

  const handleUpload = useCallback(async () => {
    if (files.length === 0) return;
    setIsLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      const input = document.querySelector<HTMLInputElement>('input[type="file"]');
      if (input && input.files) {
        Array.from(input.files).forEach((file) => {
          formData.append("files", file);
        });
      }

      const res = await fetch("/api/v1/trial/preview", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`Upload failed: ${res.status} ${text}`);
      }

      const data: ImportPreviewResponse = await res.json();
      setPreview(data);
      setStep("mapping");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed unexpectedly");
    } finally {
      setIsLoading(false);
    }
  }, [files]);

  const handleConfirmImport = useCallback(async () => {
    if (!preview) return;
    setIsLoading(true);
    setError(null);

    try {
      // In the real implementation, this would call a materialize endpoint
      // For now, we simulate success
      await new Promise((resolve) => setTimeout(resolve, 1000));
      setStep("import");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Import failed unexpectedly");
    } finally {
      setIsLoading(false);
    }
  }, [preview]);

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const renderStep = () => {
    if (step === "upload") {
      return (
        <div className="try-upload">
          <h2>Upload your receivables data</h2>
          <p className="muted">
            Drop one unpaid-invoice export or multiple customer / invoice / payment / cash snapshot files. We'll detect
            roles and suggest mappings.
          </p>

          <div className="upload-zone">
            <input
              type="file"
              multiple
              accept=".csv,.xlsx,.xls"
              onChange={handleFileSelect}
              disabled={isLoading}
            />
            <p className="muted">Supported: CSV, XLSX</p>
          </div>

          {files.length > 0 && (
            <div className="file-list">
              {files.map((f) => (
                <div key={f.name} className="file-item">
                  <span className="file-name">{f.name}</span>
                  <span className="file-size">{formatFileSize(f.size)}</span>
                </div>
              ))}
            </div>
          )}

          {error && <div className="error-banner">{error}</div>}

          <div className="step-actions">
            <button
              className="button primary"
              onClick={handleUpload}
              disabled={files.length === 0 || isLoading}
            >
              {isLoading ? "Analyzing..." : "Analyze files"}
            </button>
          </div>
        </div>
      );
    }

    if (step === "mapping" && preview) {
      return (
        <div className="try-mapping">
          <h2>Review detected mappings</h2>
          <p className="muted">
            For each file, we inferred a role and suggested canonical field mappings. Review and confirm before
            continuing.
          </p>

          {preview.files.map((file, idx) => (
            <div key={idx} className="mapping-panel">
              <div className="mapping-header">
                <span className="filename">{file.filename}</span>
                <span className="role-badge">{file.detected_role || "Unknown"}</span>
                <span className="confidence">
                  {file.detection_confidence !== null ? `${Math.round(file.detection_confidence * 100)}% confidence` : ""}
                </span>
              </div>

              {file.detection_reasons.length > 0 && (
                <div className="detection-reasons">
                  <span className="label">Detected because:</span>
                  <ul>
                    {file.detection_reasons.map((reason, i) => (
                      <li key={i}>{reason}</li>
                    ))}
                  </ul>
                </div>
              )}

              {file.required_missing.length > 0 && (
                <div className="missing-fields">
                  <span className="label warning">Missing required fields:</span>
                  <ul>
                    {file.required_missing.map((field, i) => (
                      <li key={i}>{field}</li>
                    ))}
                  </ul>
                </div>
              )}

              {file.ambiguity_warnings.length > 0 && (
                <div className="ambiguity-warnings">
                  <span className="label warning">Ambiguities:</span>
                  <ul>
                    {file.ambiguity_warnings.map((warning, i) => (
                      <li key={i}>{warning}</li>
                    ))}
                  </ul>
                </div>
              )}

              <details>
                <summary>Column mapping details</summary>
                <div className="mapping-table">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Canonical field</th>
                        <th>Source column</th>
                        <th>Confidence</th>
                        <th>Required</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(file.suggested_mapping)
                        .filter(([key]) => key !== "_alternatives")
                        .map(([canonical, mapping]: [string, unknown]) => {
                          const m = mapping as Record<string, unknown>;
                          return (
                            <tr key={canonical}>
                              <td>{canonical}</td>
                              <td>{(m.source_field as string) || "—"}</td>
                              <td>{Math.round(((m.confidence as number) || 0) * 100)}%</td>
                              <td>{m.required ? "Required" : "Optional"}</td>
                              <td>{m.resolved ? "✓" : (m.confidence as number) >= 0.5 ? "ok" : "?"}</td>
                            </tr>
                          );
                        })}
                    </tbody>
                  </table>
                </div>
              </details>

              {file.alternative_roles.length > 0 && (
                <div className="alternatives">
                  <span className="label">Alternative roles:</span>
                  <ul>
                    {file.alternative_roles.map((alt, i) => (
                      <li key={i}>
                        {alt.role} ({Math.round(alt.confidence * 100)}%)
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}

          <div className="step-actions">
            <button className="button secondary" onClick={() => setStep("upload")} disabled={isLoading}>
              Back
            </button>
            <button className="button primary" onClick={() => setStep("validation")} disabled={isLoading}>
              Continue to validation
            </button>
          </div>
        </div>
      );
    }

    if (step === "validation" && preview) {
      const q = preview.quality_profile;
      return (
        <div className="try-validation">
          <h2>Preview quality & confidence</h2>
          <p className="muted">
            Here&apos;s what we detected about your data quality and how much you can trust the outputs.
          </p>

          <div className="quality-grid">
            <div className="quality-card">
              <div className="label">Completeness</div>
              <div className="score">{Math.round((q.completeness_score || 0) * 100)}%</div>
            </div>
            <div className="quality-card">
              <div className="label">Consistency</div>
              <div className="score">{Math.round((q.consistency_score || 0) * 100)}%</div>
            </div>
            <div className="quality-card">
              <div className="label">Coverage</div>
              <div className="score">{Math.round((q.coverage_score || 0) * 100)}%</div>
            </div>
            <div className="quality-card">
              <div className="label">History depth</div>
              <div className="score">{Math.round((q.history_depth_score || 0) * 100)}%</div>
            </div>
            <div className="quality-card">
              <div className="label">Sample size</div>
              <div className="score">{Math.round((q.sample_size_score || 0) * 100)}%</div>
            </div>
          </div>

          <div className="reliability-badge">
            <span className={`grade grade-${q.reliability_grade || "insufficient"}`}>
              Reliability: {(q.reliability_grade || "insufficient").toUpperCase()}
            </span>
            <span className="overall-score">{Math.round((q.overall_confidence_score || 0) * 100)}%</span>
          </div>

          {q.recommendations.length > 0 && (
            <div className="recommendations">
              <h3>Recommendations to improve reliability</h3>
              <ul>
                {q.recommendations.map((rec, i) => (
                  <li key={i}>{rec}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="step-actions">
            <button className="button secondary" onClick={() => setStep("mapping")} disabled={isLoading}>
              Back
            </button>
            <button className="button primary" onClick={handleConfirmImport} disabled={isLoading}>
              {isLoading ? "Importing..." : "Import & score"}
            </button>
          </div>
        </div>
      );
    }

    if (step === "import") {
      return (
        <div className="try-import">
          <h2>Import complete</h2>
          <p className="muted">
            Your data has been imported into an isolated trial workspace. You can now view the dashboard, risk queue,
            and forecast for this dataset.
          </p>

          <div className="next-steps">
            <Link className="button primary" href="/">
              View dashboard
            </Link>
          </div>
        </div>
      );
    }

    return null;
  };

  return (
    <main>
      <section className="try-header">
        <div className="stepper">
          <span className={step === "upload" ? "step active" : "step"}>
            {step === "upload" ? "●" : "○"} Upload
          </span>
          <span className={step === "mapping" ? "step active" : "step"}>
            {step === "mapping" ? "●" : "○"} Mapping
          </span>
          <span className={step === "validation" ? "step active" : "step"}>
            {step === "validation" ? "●" : "○"} Validation
          </span>
          <span className={step === "import" ? "step active" : "step"}>
            {step === "import" ? "●" : "○"} Import
          </span>
        </div>
        <div className="link-row">
          <Link className="link-chip" href="/">
            ← Back to dashboard
          </Link>
          <a className="link-chip" href="/ml">
            ML evidence
          </a>
        </div>
      </section>

      <section className="try-content">{renderStep()}</section>

      <style jsx>{`
        .try-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 24px;
        }

        .stepper {
          display: flex;
          gap: 16px;
        }

        .step {
          color: var(--muted);
          font-size: 0.9rem;
        }

        .step.active {
          color: var(--accent);
          font-weight: 600;
        }

        .try-content {
          max-width: 900px;
          margin: 0 auto;
        }

        .upload-zone {
          border: 2px dashed var(--border);
          border-radius: var(--radius-lg);
          padding: 48px;
          text-align: center;
          margin: 24px 0;
        }

        .upload-zone input[type="file"] {
          display: block;
          margin: 0 auto 16px;
        }

        .file-list {
          margin: 16px 0;
        }

        .file-item {
          display: flex;
          justify-content: space-between;
          padding: 12px 16px;
          background: var(--surface);
          border-radius: var(--radius-md);
          margin-bottom: 8px;
        }

        .file-name {
          font-weight: 600;
        }

        .file-size {
          color: var(--muted);
        }

        .error-banner {
          background: var(--danger-bg);
          color: #fecdd3;
          padding: 12px 16px;
          border-radius: var(--radius-md);
          margin: 16px 0;
        }

        .step-actions {
          margin-top: 24px;
          display: flex;
          gap: 12px;
        }

        .button {
          padding: 10px 20px;
          border-radius: var(--radius-sm);
          font-weight: 600;
          cursor: pointer;
          border: none;
        }

        .button.primary {
          background: var(--primary);
          color: var(--text);
        }

        .button.secondary {
          background: transparent;
          border: 1px solid var(--border);
          color: var(--text-soft);
        }

        .button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .mapping-panel {
          background: var(--surface);
          border: 1px solid var(--border);
          border-radius: var(--radius-lg);
          padding: 20px;
          margin-bottom: 16px;
        }

        .mapping-header {
          display: flex;
          gap: 12px;
          align-items: center;
          margin-bottom: 12px;
        }

        .filename {
          font-weight: 600;
        }

        .role-badge {
          background: var(--primary-soft);
          color: var(--accent);
          padding: 4px 12px;
          border-radius: 999px;
          font-size: 0.85rem;
        }

        .confidence {
          color: var(--muted);
          font-size: 0.85rem;
        }

        .label {
          font-weight: 600;
          font-size: 0.85rem;
        }

        .label.warning {
          color: var(--warning);
        }

        .detection-reasons ul,
        .missing-fields ul,
        .ambiguity-warnings ul,
        .alternatives ul,
        .recommendations ul {
          margin: 8px 0;
          padding-left: 20px;
        }

        .detection-reasons li,
        .missing-fields li,
        .ambiguity-warnings li,
        .alternatives li,
        .recommendations li {
          margin: 4px 0;
          color: var(--text-soft);
        }

        .missing-fields li,
        .ambiguity-warnings li {
          color: var(--warning);
        }

        .mapping-table {
          margin-top: 12px;
        }

        .quality-grid {
          display: grid;
          grid-template-columns: repeat(5, 1fr);
          gap: 12px;
          margin: 24px 0;
        }

        .quality-card {
          background: var(--surface);
          border: 1px solid var(--border);
          border-radius: var(--radius-md);
          padding: 16px;
          text-align: center;
        }

        .quality-card .score {
          font-size: 1.5rem;
          font-weight: 700;
          margin-top: 8px;
        }

        .reliability-badge {
          display: flex;
          align-items: center;
          gap: 16px;
          margin: 24px 0;
        }

        .grade {
          padding: 8px 16px;
          border-radius: 999px;
          font-weight: 600;
        }

        .grade-high {
          background: var(--success-bg);
          color: #bbf7d0;
        }

        .grade-moderate {
          background: var(--warning-bg);
          color: #fde68a;
        }

        .grade-low {
          background: rgba(251, 113, 133, 0.14);
          color: #fecdd3;
        }

        .grade-insufficient {
          background: rgba(148, 163, 184, 0.14);
          color: var(--muted);
        }

        .overall-score {
          font-size: 1.5rem;
          font-weight: 700;
        }

        .recommendations {
          margin-top: 24px;
        }

        .recommendations h3 {
          font-size: 1rem;
          margin-bottom: 12px;
        }

        .try-import {
          text-align: center;
          padding: 48px 0;
        }

        .next-steps {
          margin-top: 24px;
        }

        @media (max-width: 768px) {
          .quality-grid {
            grid-template-columns: repeat(2, 1fr);
          }

          .stepper {
            flex-wrap: wrap;
            gap: 8px;
          }
        }
      `}</style>
    </main>
  );
}