"use client";

import { useAuth } from "@/providers/auth-provider";
import { useBirthProfiles } from "./use-birth-profiles";
import { useConversations } from "./use-conversations";
import { useKnowledgeOverview, useKnowledgeVersions } from "./use-knowledge";
import { usePreferences } from "./use-preferences";
import { useReports } from "./use-reports";

export function useDashboard() {
  const { user, isAuthenticated } = useAuth();
  const profiles = useBirthProfiles();
  const conversations = useConversations();
  const reports = useReports();
  const preferences = usePreferences();
  const knowledge = useKnowledgeOverview();
  const knowledgeVersions = useKnowledgeVersions();

  const isLoading =
    profiles.isLoading ||
    conversations.isLoading ||
    reports.isLoading ||
    preferences.isLoading ||
    knowledge.isLoading;

  return {
    user,
    isAuthenticated,
    profiles,
    conversations,
    reports,
    preferences,
    knowledge,
    knowledgeVersions,
    isLoading,
  };
}
