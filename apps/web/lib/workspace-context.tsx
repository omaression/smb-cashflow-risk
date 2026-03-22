"use client";

import { createContext, useContext, useState, useCallback, useEffect, ReactNode } from "react";

interface Workspace {
  id: string | null;
  label: string;
  status: string;
  hasTrialData: boolean;
}

interface WorkspaceContextValue {
  workspace: Workspace;
  isLoading: boolean;
  activateWorkspace: (workspaceId: string, label?: string) => Promise<void>;
  deactivateWorkspace: () => void;
  refreshWorkspace: () => Promise<void>;
}

const STORAGE_KEY = "smb-trial-workspace";

const WorkspaceContext = createContext<WorkspaceContextValue | undefined>(undefined);

export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const [workspace, setWorkspace] = useState<Workspace>({
    id: null,
    label: "Demo",
    status: "demo",
    hasTrialData: false,
  });
  const [isLoading, setIsLoading] = useState(false);

  // On mount, check localStorage for active workspace
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        if (parsed.id) {
          // Validate that the workspace still exists on the backend
          fetch(`/api/v1/trial/${parsed.id}/status`)
            .then((res) => {
              if (res.ok) {
                setWorkspace({
                  id: parsed.id,
                  label: parsed.label || "Trial Workspace",
                  status: parsed.status || "imported",
                  hasTrialData: true,
                });
              } else {
                // Workspace no longer exists, clear localStorage
                console.warn("Stored workspace no longer exists, clearing");
                localStorage.removeItem(STORAGE_KEY);
              }
            })
            .catch(() => {
              // Network error, keep stored workspace but log warning
              console.warn("Failed to validate stored workspace");
            });
        }
      } catch {
        localStorage.removeItem(STORAGE_KEY);
      }
    }
  }, []);

  const activateWorkspace = useCallback(async (workspaceId: string, label?: string) => {
    setIsLoading(true);
    try {
      // Fetch workspace status from API to validate it exists
      const res = await fetch(`/api/v1/trial/${workspaceId}/status`);
      if (res.ok) {
        const data = await res.json();
        const ws: Workspace = {
          id: workspaceId,
          label: label || data.label || "Trial Workspace",
          status: data.status || "imported",
          hasTrialData: true,
        };
        setWorkspace(ws);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(ws));
      } else if (res.status === 404) {
        // Workspace not found, clear localStorage and stay in demo mode
        console.warn("Workspace not found, staying in demo mode");
        localStorage.removeItem(STORAGE_KEY);
        setWorkspace({
          id: null,
          label: "Demo",
          status: "demo",
          hasTrialData: false,
        });
      } else {
        // Other error, activate with basic info but log warning
        console.warn("Failed to fetch workspace status, activating anyway");
        const ws: Workspace = {
          id: workspaceId,
          label: label || "Trial Workspace",
          status: "imported",
          hasTrialData: true,
        };
        setWorkspace(ws);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(ws));
      }
    } catch (err) {
      console.error("Failed to activate workspace:", err);
      // Don't activate on error - stay in demo mode
      localStorage.removeItem(STORAGE_KEY);
      setWorkspace({
        id: null,
        label: "Demo",
        status: "demo",
        hasTrialData: false,
      });
    } finally {
      setIsLoading(false);
    }
  }, []);

  const deactivateWorkspace = useCallback(() => {
    setWorkspace({
      id: null,
      label: "Demo",
      status: "demo",
      hasTrialData: false,
    });
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  const refreshWorkspace = useCallback(async () => {
    if (!workspace.id) return;
    try {
      const res = await fetch(`/api/v1/trial/${workspace.id}/status`);
      if (res.ok) {
        const data = await res.json();
        setWorkspace((prev) => ({
          ...prev,
          status: data.status || prev.status,
          label: data.label || prev.label,
        }));
      }
    } catch (err) {
      console.error("Failed to refresh workspace:", err);
    }
  }, [workspace.id]);

  return (
    <WorkspaceContext.Provider
      value={{
        workspace,
        isLoading,
        activateWorkspace,
        deactivateWorkspace,
        refreshWorkspace,
      }}
    >
      {children}
    </WorkspaceContext.Provider>
  );
}

export function useWorkspace() {
  const context = useContext(WorkspaceContext);
  if (context === undefined) {
    throw new Error("useWorkspace must be used within a WorkspaceProvider");
  }
  return context;
}