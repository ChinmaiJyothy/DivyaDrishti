"use client";

import { Loader2, Plus, Trash2, Users } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { useBirthProfiles, useCreateBirthProfile, useDeleteBirthProfile } from "@/hooks/use-birth-profiles";
import { useSettings } from "@/providers/settings-provider";
import type { BirthProfile } from "@/types";

export default function ProfilesPage() {
  const { data: profiles, isLoading } = useBirthProfiles();
  const create = useCreateBirthProfile();
  const deleteProfile = useDeleteBirthProfile();
  const { setCurrentProfileId } = useSettings();
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({
    profile_name: "",
    relationship: "self",
    date_of_birth: "",
    time_of_birth: "",
    birth_place: "",
    latitude: "",
    longitude: "",
    timezone: "Asia/Kolkata",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await create.mutateAsync({
      profile_name: form.profile_name,
      relationship: form.relationship,
      date_of_birth: form.date_of_birth,
      time_of_birth: form.time_of_birth || undefined,
      birth_place: form.birth_place || undefined,
      latitude: form.latitude ? Number(form.latitude) : undefined,
      longitude: form.longitude ? Number(form.longitude) : undefined,
      timezone: form.timezone,
    });
    setOpen(false);
  };

  if (isLoading) {
    return (
      <div className="space-y-6 pb-20">
        <h1 className="text-2xl font-bold">Birth Profiles</h1>
        <Skeleton className="h-40 w-full" />
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-20">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Birth Profiles</h1>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button size="sm">
              <Plus className="mr-2 h-4 w-4" />
              Add Profile
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-lg">
            <DialogHeader>
              <DialogTitle>Create Birth Profile</DialogTitle>
              <DialogDescription>Add a new profile to your workspace.</DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="profile_name">Name</Label>
                <Input id="profile_name" value={form.profile_name} onChange={(e) => setForm({ ...form, profile_name: e.target.value })} required />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="date_of_birth">Date of Birth</Label>
                  <Input id="date_of_birth" type="date" value={form.date_of_birth} onChange={(e) => setForm({ ...form, date_of_birth: e.target.value })} required />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="time_of_birth">Time of Birth</Label>
                  <Input id="time_of_birth" type="time" value={form.time_of_birth} onChange={(e) => setForm({ ...form, time_of_birth: e.target.value })} />
                </div>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="birth_place">Birth Place</Label>
                <Input id="birth_place" value={form.birth_place} onChange={(e) => setForm({ ...form, birth_place: e.target.value })} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="latitude">Latitude</Label>
                  <Input id="latitude" type="number" step="any" value={form.latitude} onChange={(e) => setForm({ ...form, latitude: e.target.value })} />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="longitude">Longitude</Label>
                  <Input id="longitude" type="number" step="any" value={form.longitude} onChange={(e) => setForm({ ...form, longitude: e.target.value })} />
                </div>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="timezone">Timezone</Label>
                <Input id="timezone" value={form.timezone} onChange={(e) => setForm({ ...form, timezone: e.target.value })} />
              </div>
              <Button type="submit" disabled={create.isPending}>
                {create.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Create Profile
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {!profiles || profiles.length === 0 ? (
        <EmptyState icon={Users} title="No profiles" description="Add a birth profile to get started." />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {profiles.map((profile) => (
            <ProfileCard key={profile.id} profile={profile} onSelect={setCurrentProfileId} onDelete={deleteProfile.mutateAsync} />
          ))}
        </div>
      )}
    </div>
  );
}

function ProfileCard({
  profile,
  onSelect,
  onDelete,
}: {
  profile: BirthProfile;
  onSelect: (id: string) => void;
  onDelete: (id: string) => Promise<void>;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">{profile.profile_name}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        <p className="text-sm capitalize text-muted-foreground">{profile.relationship}</p>
        <p className="text-sm text-muted-foreground">{profile.date_of_birth}</p>
        <p className="text-sm text-muted-foreground">{profile.birth_place}</p>
        <div className="flex gap-2 pt-2">
          <Button variant="outline" size="sm" onClick={() => onSelect(String(profile.id))}>
            Select
          </Button>
          <Button variant="ghost" size="icon" onClick={() => onDelete(profile.id)}>
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
