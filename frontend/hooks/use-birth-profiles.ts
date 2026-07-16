"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  analyzeChart,
  createProfile,
  deleteProfile,
  generateChart,
  getLatestProfileChart,
  getProfile,
  getProfileCharts,
  getProfiles,
  getStudioDetail,
  searchChart,
  updateProfile,
  type CreateBirthProfileInput,
  type UpdateBirthProfileInput,
} from "@/services/birth-profile.service";
import type { BirthChart, BirthProfile, StudioChartDetail, StudioInsight } from "@/types";

const QUERY_KEY = ["birth-profiles"];

export function useBirthProfiles() {
  return useQuery<BirthProfile[]>({
    queryKey: QUERY_KEY,
    queryFn: getProfiles,
    retry: 1,
  });
}

export function useBirthProfile(id: string) {
  return useQuery<BirthProfile>({
    queryKey: [...QUERY_KEY, id],
    queryFn: () => getProfile(id),
    enabled: !!id,
    retry: 1,
  });
}

export function useProfileCharts(id: string) {
  return useQuery<BirthChart[]>({
    queryKey: [...QUERY_KEY, id, "charts"],
    queryFn: () => getProfileCharts(id),
    enabled: !!id,
    retry: 1,
  });
}

export function useLatestProfileChart(id: string, chartType = "rashi") {
  return useQuery<BirthChart>({
    queryKey: [...QUERY_KEY, id, "charts", "latest", chartType],
    queryFn: () => getLatestProfileChart(id, chartType),
    enabled: !!id,
    retry: 1,
  });
}

export function useGenerateChart(id: string) {
  const queryClient = useQueryClient();

  return useMutation<BirthChart, Error, string>({
    mutationFn: (chartType) => generateChart(id, chartType),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [...QUERY_KEY, id, "charts"] });
    },
  });
}

export function useStudio(chartId: string, question?: string) {
  return useQuery<StudioChartDetail>({
    queryKey: ["studio", chartId, question ?? ""],
    queryFn: () => getStudioDetail(chartId, question),
    enabled: !!chartId,
    retry: 1,
  });
}

export function useAnalyzeChart(chartId: string) {
  return useMutation<StudioInsight, Error, string>({
    mutationFn: (question) => analyzeChart(chartId, question),
  });
}

export function useSearchChart(chartId: string) {
  return useMutation<Array<Record<string, unknown>>, Error, string>({
    mutationFn: (q) => searchChart(chartId, q),
  });
}

export function useCreateBirthProfile() {
  const queryClient = useQueryClient();

  return useMutation<BirthProfile, Error, CreateBirthProfileInput>({
    mutationFn: createProfile,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
    },
  });
}

export function useUpdateBirthProfile(id: string) {
  const queryClient = useQueryClient();

  return useMutation<BirthProfile, Error, UpdateBirthProfileInput>({
    mutationFn: (input) => updateProfile(id, input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
    },
  });
}

export function useDeleteBirthProfile() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>({
    mutationFn: deleteProfile,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
    },
  });
}
