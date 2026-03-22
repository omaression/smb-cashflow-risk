"use client";

import { ReactNode } from "react";
import { WorkspaceProvider } from "@/lib/workspace-context";

export function Providers({ children }: { children: ReactNode }) {
  return <WorkspaceProvider>{children}</WorkspaceProvider>;
}