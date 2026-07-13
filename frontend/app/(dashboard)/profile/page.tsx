"use client";

import { User } from "lucide-react";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/providers/auth-provider";

export default function ProfilePage() {
  const { user, logout } = useAuth();

  return (
    <div className="space-y-6 pb-20">
      <h1 className="text-2xl font-bold">User Profile</h1>
      <Card>
        <CardHeader className="flex flex-row items-center gap-4">
          <Avatar className="h-16 w-16">
            <AvatarFallback className="text-xl">{user?.name?.charAt(0)?.toUpperCase() || "U"}</AvatarFallback>
          </Avatar>
          <div>
            <CardTitle>{user?.name}</CardTitle>
            <p className="text-sm text-muted-foreground">{user?.email}</p>
            <p className="text-sm capitalize text-muted-foreground">{user?.role}</p>
          </div>
        </CardHeader>
        <CardContent>
          <Button variant="outline" onClick={() => logout()}>
            <User className="mr-2 h-4 w-4" />
            Sign out
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
