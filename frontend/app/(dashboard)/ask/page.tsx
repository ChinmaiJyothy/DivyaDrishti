"use client";

import { Loader2, Send } from "lucide-react";
import { useState } from "react";

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
import { useCreateConversation } from "@/hooks/use-conversations";
import { useToast } from "@/hooks/use-toast";

export default function AskPage() {
  const create = useCreateConversation();
  const toast = useToast();
  const [question, setQuestion] = useState("");
  const [domain, setDomain] = useState("general");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await create.mutateAsync({ title: question, domain });
    toast.success("Conversation started");
    setQuestion("");
  };

  return (
    <div className="space-y-6 pb-20">
      <h1 className="text-2xl font-bold">Ask DivyaDrishti</h1>
      <Card>
        <CardHeader>
          <CardTitle>What would you like to know?</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="question">Your Question</Label>
              <Input
                id="question"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask about career, marriage, health, finance..."
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="domain">Category</Label>
              <Select value={domain} onValueChange={setDomain}>
                <SelectTrigger id="domain">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="general">General</SelectItem>
                  <SelectItem value="career">Career</SelectItem>
                  <SelectItem value="marriage">Marriage</SelectItem>
                  <SelectItem value="finance">Finance</SelectItem>
                  <SelectItem value="health">Health</SelectItem>
                  <SelectItem value="compatibility">Compatibility</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button type="submit" disabled={create.isPending || !question.trim()}>
              {create.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              <Send className="mr-2 h-4 w-4" />
              Ask
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
