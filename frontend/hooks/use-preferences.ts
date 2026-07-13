"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { getPreferences, updatePreferences, type PreferenceUpdateInput } from "@/services/preference.service";
import type { Preference } from "@/types";

const QUERY_KEY = ["preferences"];

export function usePreferences() {
  return useQuery<Preference>({
    queryKey: QUERY_KEY,
    queryFn: getPreferences,
    retry: 1,
  });
}

export function useUpdatePreferences() {
  const queryClient = useQueryClient();

  return useMutation<Preference, Error, PreferenceUpdateInput>({
    mutationFn: updatePreferences,
    onSuccess: (data) => {
      queryClient.setQueryData(QUERY_KEY, data);
    },
  });
}
