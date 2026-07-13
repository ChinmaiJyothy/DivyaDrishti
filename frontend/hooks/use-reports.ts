"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createReport,
  deleteReport,
  getReports,
  updateReport,
  type CreateReportInput,
  type UpdateReportInput,
} from "@/services/report.service";
import type { Report } from "@/types";

const QUERY_KEY = ["reports"];

export function useReports() {
  return useQuery<Report[]>({
    queryKey: QUERY_KEY,
    queryFn: getReports,
    retry: 1,
  });
}

export function useCreateReport() {
  const queryClient = useQueryClient();

  return useMutation<Report, Error, CreateReportInput>({
    mutationFn: createReport,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
    },
  });
}

export function useUpdateReport(id: string) {
  const queryClient = useQueryClient();

  return useMutation<Report, Error, UpdateReportInput>({
    mutationFn: (input) => updateReport(id, input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
    },
  });
}

export function useDeleteReport() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>({
    mutationFn: deleteReport,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
    },
  });
}
