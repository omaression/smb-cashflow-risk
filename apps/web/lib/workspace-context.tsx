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
          setWorkspace({
            id: parsed.id,
            label: parsed.label || "Trial Workspace",
            status: parsed.status || "imported",
            hasTrialData: true,
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
      // Fetch workspace status from API
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
      } else {
        // If fetch fails, still activate with basic info
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
      // Activate anyway with basic info
      const ws: Workspace = {
        id: workspaceId,
        label: label || "Trial Workspace",
        status: "imported",
        hasTrialData: true,
      };
      setWorkspace(ws);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(ws));
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