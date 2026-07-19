"use client";

import { Loader2, Plus, Users, AlertCircle } from "lucide-react";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
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
import { EmptyState } from "@/components/ui/empty-state";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  useBirthProfiles,
  useCreateBirthProfile,
  useGenerateChart,
  useLatestProfileChart,
} from "@/hooks/use-birth-profiles";
import { useSettings } from "@/providers/settings-provider";
import type { BirthProfile } from "@/types";

function CreateProfileDialog({
  onCreated,
}: {
  onCreated: (profile: BirthProfile) => void;
}) {
  const [open, setOpen] = useState(false);
  const create = useCreateBirthProfile();
  const [form, setForm] = useState({
    profile_name: "",
    relationship: "self",
    date_of_birth: "",
    time_of_birth: "",
    birth_place: "",
    latitude: "",
    longitude: "",
    timezone: "Asia/Kolkata",
    accuracy_level: "exact",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = await create.mutateAsync({
      profile_name: form.profile_name,
      relationship: form.relationship,
      date_of_birth: form.date_of_birth,
      time_of_birth: form.time_of_birth || undefined,
      birth_place: form.birth_place || undefined,
      latitude: form.latitude ? Number(form.latitude) : undefined,
      longitude: form.longitude ? Number(form.longitude) : undefined,
      timezone: form.timezone,
      accuracy_level: form.accuracy_level,
    });
    onCreated(result);
    setOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="sm" className="gap-1">
          <Plus className="h-4 w-4" />
          Create
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Create Birth Profile</DialogTitle>
          <DialogDescription>
            Add a new birth profile to your workspace.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="profile_name">Name</Label>
            <Input
              id="profile_name"
              value={form.profile_name}
              onChange={(e) => setForm({ ...form, profile_name: e.target.value })}
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label htmlFor="date_of_birth">Date of Birth</Label>
              <Input
                id="date_of_birth"
                type="date"
                value={form.date_of_birth}
                onChange={(e) => setForm({ ...form, date_of_birth: e.target.value })}
                required
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="time_of_birth">Time of Birth</Label>
              <Input
                id="time_of_birth"
                type="time"
                value={form.time_of_birth}
                onChange={(e) => setForm({ ...form, time_of_birth: e.target.value })}
              />
            </div>
          </div>
          <div className="grid gap-2">
            <Label htmlFor="birth_place">Birth Place</Label>
            <Input
              id="birth_place"
              value={form.birth_place}
              onChange={(e) => setForm({ ...form, birth_place: e.target.value })}
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <Label htmlFor="latitude">Latitude</Label>
              <Input
                id="latitude"
                type="number"
                step="any"
                value={form.latitude}
                onChange={(e) => setForm({ ...form, latitude: e.target.value })}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="longitude">Longitude</Label>
              <Input
                id="longitude"
                type="number"
                step="any"
                value={form.longitude}
                onChange={(e) => setForm({ ...form, longitude: e.target.value })}
              />
            </div>
          </div>
          <div className="grid gap-2">
            <Label htmlFor="timezone">Timezone</Label>
            <Input
              id="timezone"
              value={form.timezone}
              onChange={(e) => setForm({ ...form, timezone: e.target.value })}
            />
          </div>
          <Button type="submit" disabled={create.isPending}>
            {create.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Create Profile
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function ProfileSwitcher({
  profiles,
  currentId,
  onChange,
}: {
  profiles: BirthProfile[];
  currentId: string | null;
  onChange: (id: string) => void;
}) {
  return (
    <Select value={currentId || ""} onValueChange={onChange}>
      <SelectTrigger className="h-8 text-xs" aria-label="Switch profile">
        <SelectValue placeholder="Select profile" />
      </SelectTrigger>
      <SelectContent>
        {profiles.map((profile) => (
          <SelectItem key={String(profile.id)} value={String(profile.id)}>
            {profile.profile_name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}

export function BirthProfileCard() {
  const { data: profiles, isLoading, error } = useBirthProfiles();
  const { settings, setCurrentProfileId } = useSettings();
  const currentId = settings.currentProfileId;
  const { data: chart, isLoading: chartLoading } = useLatestProfileChart(currentId || "");
  const generate = useGenerateChart(currentId || "");

  useEffect(() => {
    if (profiles && profiles.length > 0 && !currentId) {
      setCurrentProfileId(String(profiles[0].id));
    }
  }, [profiles, currentId, setCurrentProfileId]);

  const currentProfile = profiles?.find((p) => String(p.id) === currentId);

  const handleGenerate = () => {
    generate.reset();
    generate.mutate("rashi");
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-5 w-32" />
        </CardHeader>
        <CardContent className="space-y-2">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-2/3" />
        </CardContent>
      </Card>
    );
  }

  if (error || !profiles || profiles.length === 0) {
    return (
      <Card>
        <CardContent className="py-6">
          <EmptyState
            icon={Users}
            title="No birth profile"
            description="Create a birth profile to see personalized insights."
          />
          <div className="mt-4 flex justify-center">
            <CreateProfileDialog onCreated={(p) => setCurrentProfileId(String(p.id))} />
          </div>
        </CardContent>
      </Card>
    );
  }

  const chartData = chart?.chart_data ?? {};
  const hasChartData = chart?.chart_data && Object.keys(chart.chart_data).length > 0;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between gap-2">
        <CardTitle className="text-base">Current Profile</CardTitle>
        <CreateProfileDialog onCreated={(p) => setCurrentProfileId(String(p.id))} />
      </CardHeader>
      <CardContent className="space-y-4">
        <ProfileSwitcher
          profiles={profiles}
          currentId={currentId}
          onChange={(id) => setCurrentProfileId(id)}
        />

        {currentProfile && (
          <div className="space-y-1">
            <p className="text-lg font-semibold">{currentProfile.profile_name}</p>
            <p className="text-sm capitalize text-muted-foreground">
              {currentProfile.relationship}
            </p>
            <p className="text-sm text-muted-foreground">
              {currentProfile.date_of_birth} {currentProfile.time_of_birth}
            </p>
            <p className="text-sm text-muted-foreground">{currentProfile.birth_place}</p>
          </div>
        )}

        {chartLoading ? (
          <div className="space-y-2">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
          </div>
        ) : hasChartData ? (
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="rounded-lg bg-muted p-2">
              <span className="block text-xs text-muted-foreground">Lagna</span>
              <span className="font-medium">{(chartData as { lagna?: string }).lagna || "—"}</span>
            </div>
            <div className="rounded-lg bg-muted p-2">
              <span className="block text-xs text-muted-foreground">Moon Sign</span>
              <span className="font-medium">{(chartData as { moon_sign?: string }).moon_sign || "—"}</span>
            </div>
            <div className="col-span-2 rounded-lg bg-muted p-2">
              <span className="block text-xs text-muted-foreground">Current Mahadasha</span>
              <span className="font-medium">
                {(chartData as { maha_dasha?: string }).maha_dasha || "—"}
              </span>
            </div>
          </div>
        ) : (
          <div className="space-y-3 text-center">
            <p className="text-sm text-muted-foreground">No birth chart generated yet.</p>
            <Button size="sm" onClick={handleGenerate} disabled={generate.isPending}>
              {generate.isPending ? "Generating..." : "Generate Birth Chart"}
            </Button>
            {generate.isError && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Chart generation failed</AlertTitle>
                <AlertDescription>
                  {generate.error?.message || "An unexpected error occurred."}
                </AlertDescription>
              </Alert>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
