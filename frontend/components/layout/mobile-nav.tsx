"use client";

import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerHeader,
  DrawerTitle,
} from "@/components/ui/drawer";

interface MobileNavProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  children: React.ReactNode;
}

export function MobileNav({ open, onOpenChange, children }: MobileNavProps) {
  return (
    <Drawer open={open} onOpenChange={onOpenChange}>
      <DrawerContent className="h-[80vh]">
        <DrawerHeader className="text-left">
          <DrawerTitle className="font-display">DivyaDrishti</DrawerTitle>
        </DrawerHeader>
        <div className="flex flex-col gap-2 p-4">{children}</div>
      </DrawerContent>
    </Drawer>
  );
}
