import { PlanetaryOverview } from "@/components/dashboard/planetary-overview";

export default function ChartsPage() {
  return (
    <div className="space-y-6 pb-20">
      <h1 className="text-2xl font-bold">Birth Charts</h1>
      <PlanetaryOverview />
    </div>
  );
}
