"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createProfile,
  deleteProfile,
  getLatestProfileChart,
  getProfile,
  getProfileCharts,
  getProfiles,
  updateProfile,
  type CreateBirthProfileInput,
  type UpdateBirthProfileInput,
} from "@/services/birth-profile.service";
import type { BirthChart, BirthProfile } from "@/types";

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

export function useLatestProfileChart(id: string) {
  return useQuery<BirthChart>({
    queryKey: [...QUERY_KEY, id, "charts", "latest"],
    queryFn: () => getLatestProfileChart(id),
    enabled: !!id,
    retry: 1,
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
