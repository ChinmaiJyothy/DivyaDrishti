"use client";

import { BookOpen, Loader2, Trash2, Upload } from "lucide-react";
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { useBooks, useDeleteBook, useUploadBook } from "@/hooks/use-knowledge";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/providers/auth-provider";

function UploadBookDialog() {
  const [open, setOpen] = useState(false);
  const upload = useUploadBook();
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    await upload.mutateAsync({ file, title });
    setOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="sm" className="gap-1">
          <Upload className="h-4 w-4" />
          Upload
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Upload Knowledge Book</DialogTitle>
          <DialogDescription>
            Upload a Vedic astrology text to expand the knowledge base.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="title">Title</Label>
            <Input id="title" value={title} onChange={(e) => setTitle(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="file">File</Label>
            <Input
              id="file"
              type="file"
              accept=".pdf,.epub,.txt"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
            />
          </div>
          <Button type="submit" disabled={upload.isPending || !file}>
            {upload.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Upload Book
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export function KnowledgeCard() {
  const { data: books, isLoading } = useBooks();
  const deleteBook = useDeleteBook();
  const toast = useToast();
  const { user } = useAuth();
  const isAdmin = user?.is_superuser || user?.role === "admin" || user?.role === "super_admin";

  const handleDelete = async (id: string) => {
    await deleteBook.mutateAsync(id);
    toast.success("Book removed");
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-5 w-40" />
        </CardHeader>
        <CardContent className="space-y-3">
          <Skeleton className="h-14 w-full" />
          <Skeleton className="h-14 w-full" />
        </CardContent>
      </Card>
    );
  }

  if (!books || books.length === 0) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-base">Knowledge Library</CardTitle>
          {isAdmin && <UploadBookDialog />}
        </CardHeader>
        <CardContent className="py-4">
          <EmptyState
            icon={BookOpen}
            title="No books uploaded"
            description="Upload Vedic texts to power the knowledge base."
          />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-base">Knowledge Library</CardTitle>
        {isAdmin && <UploadBookDialog />}
      </CardHeader>
      <CardContent className="space-y-3">
        {books.slice(0, 5).map((book) => (
          <div
            key={book.id}
            className="flex items-center justify-between rounded-lg border p-3 transition-colors hover:bg-muted/50"
          >
            <div className="min-w-0">
              <p className="truncate font-medium">{book.title || book.file_name}</p>
              <p className="text-xs text-muted-foreground">
                {book.author || "Unknown"} • {book.language || "—"} • {book.status}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant={book.is_active ? "default" : "secondary"}>
                {book.is_active ? "Active" : "Inactive"}
              </Badge>
              {isAdmin && (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => handleDelete(book.id)}
                  disabled={deleteBook.isPending}
                  aria-label="Delete book"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              )}
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
