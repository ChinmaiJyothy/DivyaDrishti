import { toast } from "sonner";

export function useToast() {
  return {
    toast,
    success: (message: string, options?: Parameters<typeof toast>[1]) => toast.success(message, options),
    error: (message: string, options?: Parameters<typeof toast>[1]) => toast.error(message, options),
    info: (message: string, options?: Parameters<typeof toast>[1]) => toast.info(message, options),
  };
}
