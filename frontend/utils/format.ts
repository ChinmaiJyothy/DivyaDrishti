export function formatDate(input: string | number | Date): string {
  const date = new Date(input);
  return date.toLocaleDateString("en-IN", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}
