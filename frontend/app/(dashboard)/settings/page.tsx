"use client";

import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { usePreferences, useUpdatePreferences } from "@/hooks/use-preferences";
import { useToast } from "@/hooks/use-toast";

export default function SettingsPage() {
  const { data: preferences, isLoading } = usePreferences();
  const update = useUpdatePreferences();
  const toast = useToast();
  const [form, setForm] = useState<Partial<import("@/types").Preference>>({});

  useEffect(() => {
    if (preferences) {
      setForm({ ...preferences });
    }
  }, [preferences]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await update.mutateAsync(form);
    toast.success("Preferences updated");
  };

  if (isLoading) {
    return (
      <div className="space-y-6 pb-20">
        <h1 className="text-2xl font-bold">Settings</h1>
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-20">
      <h1 className="text-2xl font-bold">Settings</h1>
      <form onSubmit={handleSubmit}>
        <Card>
          <CardHeader>
            <CardTitle>Preferences</CardTitle>
          </CardHeader>
          <CardContent className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="preferred_language">Language</Label>
              <Select
                value={(form.preferred_language as string) || "en"}
                onValueChange={(value) => setForm({ ...form, preferred_language: value })}
              >
                <SelectTrigger id="preferred_language">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="en">English</SelectItem>
                  <SelectItem value="hi">Hindi</SelectItem>
                  <SelectItem value="sa">Sanskrit</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="preferred_explanation_depth">Explanation Depth</Label>
              <Select
                value={(form.preferred_explanation_depth as string) || "moderate"}
                onValueChange={(value) => setForm({ ...form, preferred_explanation_depth: value })}
              >
                <SelectTrigger id="preferred_explanation_depth">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="basic">Basic</SelectItem>
                  <SelectItem value="moderate">Moderate</SelectItem>
                  <SelectItem value="detailed">Detailed</SelectItem>
                  <SelectItem value="scholarly">Scholarly</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="preferred_astrology_school">Astrology School</Label>
              <Select
                value={(form.preferred_astrology_school as string) || "parashari"}
                onValueChange={(value) => setForm({ ...form, preferred_astrology_school: value })}
              >
                <SelectTrigger id="preferred_astrology_school">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="parashari">Parashari</SelectItem>
                  <SelectItem value="jamini">Jaimini</SelectItem>
                  <SelectItem value="tajik">Tajik</SelectItem>
                  <SelectItem value="kp">KP</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="preferred_chart_style">Chart Style</Label>
              <Select
                value={(form.preferred_chart_style as string) || "north_indian"}
                onValueChange={(value) => setForm({ ...form, preferred_chart_style: value })}
              >
                <SelectTrigger id="preferred_chart_style">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="north_indian">North Indian</SelectItem>
                  <SelectItem value="south_indian">South Indian</SelectItem>
                  <SelectItem value="western">Western</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="timezone">Timezone</Label>
              <Input
                id="timezone"
                value={(form.timezone as string) || ""}
                onChange={(e) => setForm({ ...form, timezone: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="country">Country</Label>
              <Input
                id="country"
                value={(form.country as string) || ""}
                onChange={(e) => setForm({ ...form, country: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="citation_mode">Citation Mode</Label>
              <Select
                value={(form.citation_mode as string) || "cited"}
                onValueChange={(value) => setForm({ ...form, citation_mode: value })}
              >
                <SelectTrigger id="citation_mode">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="cited">Cited</SelectItem>
                  <SelectItem value="uncited">Uncited</SelectItem>
                  <SelectItem value="sourced">Sourced</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="units">Units</Label>
              <Select
                value={(form.units as string) || "metric"}
                onValueChange={(value) => setForm({ ...form, units: value })}
              >
                <SelectTrigger id="units">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="metric">Metric</SelectItem>
                  <SelectItem value="imperial">Imperial</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="sm:col-span-2">
              <Button type="submit" disabled={update.isPending}>
                {update.isPending ? "Saving..." : "Save Preferences"}
              </Button>
            </div>
          </CardContent>
        </Card>
      </form>
    </div>
  );
}
