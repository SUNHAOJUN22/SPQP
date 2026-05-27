import type { Toast } from "@/lib/store";

export function actionToast(type: Toast["type"], message: string): Omit<Toast, "id"> {
  return { type, message, duration: type === "error" ? 6000 : 3600 };
}
