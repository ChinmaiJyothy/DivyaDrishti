"use client";

import { useMemo } from "react";

import { cn } from "@/lib/utils";
import type { BirthChartData, PlanetPosition } from "@/types";

const SIGN_LAYOUT = [
  ["Pisces", "Aries", "Taurus", "Gemini"],
  ["Aquarius", "Cancer", "Leo", "Virgo"],
  ["Capricorn", "Sagittarius", "Scorpio", "Libra"],
];

const SIGN_SYMBOLS: Record<string, string> = {
  Aries: "Ari",
  Taurus: "Tau",
  Gemini: "Gem",
  Cancer: "Can",
  Leo: "Leo",
  Virgo: "Vir",
  Libra: "Lib",
  Scorpio: "Sco",
  Sagittarius: "Sag",
  Capricorn: "Cap",
  Aquarius: "Aqu",
  Pisces: "Pis",
};

const PLANET_SYMBOLS: Record<string, string> = {
  Sun: "Su",
  Moon: "Mo",
  Mars: "Ma",
  Mercury: "Me",
  Jupiter: "Ju",
  Venus: "Ve",
  Saturn: "Sa",
  Rahu: "Ra",
  Ketu: "Ke",
};

const PLANET_COLORS: Record<string, string> = {
  Sun: "#f97316",
  Moon: "#94a3b8",
  Mars: "#ef4444",
  Mercury: "#10b981",
  Jupiter: "#facc15",
  Venus: "#ec4899",
  Saturn: "#1f2937",
  Rahu: "#6366f1",
  Ketu: "#64748b",
};

interface BirthChartSvgProps {
  data: BirthChartData;
  className?: string;
  selectedId?: string;
  selectedType?: "planet" | "sign" | "house";
  onSelect?: (selection: { type: "planet" | "sign" | "house"; id: string }) => void;
}

export function BirthChartSvg({
  data,
  className,
  selectedId,
  selectedType,
  onSelect,
}: BirthChartSvgProps) {
  const planetsBySign = useMemo(() => {
    const map = new Map<string, PlanetPosition[]>();
    for (const sign of SIGN_LAYOUT.flat()) {
      map.set(sign, []);
    }
    for (const [name, pos] of Object.entries(data.planets)) {
      if (!pos.sign) continue;
      const list = map.get(pos.sign) ?? [];
      list.push({ ...pos, name });
      map.set(pos.sign, list);
    }
    return map;
  }, [data.planets]);

  const houseNumberBySign = useMemo(() => {
    const lagnaSign = data.lagna;
    const map = new Map<string, number>();
    const flat = SIGN_LAYOUT.flat();
    const lagnaIndex = flat.indexOf(lagnaSign);
    for (let i = 0; i < 12; i++) {
      const sign = flat[(lagnaIndex + i) % 12];
      map.set(sign, i + 1);
    }
    return map;
  }, [data.lagna]);

  const width = 480;
  const height = 360;
  const cols = 4;
  const rows = 3;
  const cellW = width / cols;
  const cellH = height / rows;
  const pad = 4;

  const handleCellClick = (sign: string) => {
    onSelect?.({ type: "sign", id: sign });
  };

  const handlePlanetClick = (name: string, sign: string, e: React.SyntheticEvent) => {
    e.stopPropagation();
    onSelect?.({ type: "planet", id: name });
  };

  const handleHouseClick = (house: number, sign: string, e: React.SyntheticEvent) => {
    e.stopPropagation();
    onSelect?.({ type: "house", id: String(house) });
  };

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      className={cn("w-full h-auto rounded-md border bg-card", className)}
      role="img"
      aria-label="Interactive birth chart"
      tabIndex={0}
    >
      <defs>
        <pattern id="ascendant" patternUnits="userSpaceOnUse" width={10} height={10}>
          <path d="M0,10 L10,0" stroke="currentColor" strokeWidth={1} opacity={0.3} />
        </pattern>
      </defs>

      {SIGN_LAYOUT.map((row, r) =>
        row.map((sign, c) => {
          const x = c * cellW;
          const y = r * cellH;
          const house = houseNumberBySign.get(sign);
          const isLagna = sign === data.lagna;
          const isSelected = selectedType === "sign" && selectedId === sign;
          const planets = planetsBySign.get(sign) ?? [];
          const planetCols = planets.length <= 2 ? 1 : 2;

          return (
            <g
              key={sign}
              transform={`translate(${x}, ${y})`}
              onClick={() => handleCellClick(sign)}
              className="cursor-pointer focus:outline-none"
              tabIndex={0}
              role="button"
              aria-label={`${sign}, house ${house}`}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  handleCellClick(sign);
                }
              }}
            >
              <rect
                width={cellW - pad * 2}
                height={cellH - pad * 2}
                x={pad}
                y={pad}
                rx={6}
                className={cn(
                  "transition-all duration-200",
                  isLagna ? "fill-primary/10 stroke-primary" : "fill-card stroke-border",
                  isSelected && "fill-primary/20 stroke-primary ring-2"
                )}
                strokeWidth={isLagna || isSelected ? 2 : 1}
              />

              <text
                x={pad + 8}
                y={pad + 16}
                className="text-[10px] font-semibold fill-muted-foreground"
              >
                {SIGN_SYMBOLS[sign]}
              </text>

              {house && (
                <text
                  x={cellW - pad - 8}
                  y={pad + 16}
                  textAnchor="end"
                  className="text-[10px] font-semibold fill-primary cursor-pointer"
                  onClick={(e) => handleHouseClick(house, sign, e)}
                  role="button"
                  aria-label={`House ${house}`}
                >
                  H{house}
                </text>
              )}

              {planets.length > 0 && (
                <g transform={`translate(${cellW / 2}, ${cellH / 2 + 6})`}>
                  {planets.map((planet, index) => {
                    const cols = planetCols;
                    const row = Math.floor(index / cols);
                    const col = index % cols;
                    const offsetX = (col - (cols - 1) / 2) * 28;
                    const offsetY = (row - (Math.ceil(planets.length / cols) - 1) / 2) * 24;
                    const isPlanetSelected = selectedType === "planet" && selectedId === planet.name;

                    return (
                      <g
                        key={planet.name}
                        transform={`translate(${offsetX}, ${offsetY})`}
                        onClick={(e) => handlePlanetClick(planet.name ?? "", sign, e)}
                        className="cursor-pointer"
                        role="button"
                        aria-label={planet.name}
                        tabIndex={0}
                        onKeyDown={(e) => {
                          if (e.key === "Enter" || e.key === " ") {
                            e.preventDefault();
                            handlePlanetClick(planet.name ?? "", sign, e);
                          }
                        }}
                      >
                        <circle
                          r={12}
                          fill={PLANET_COLORS[planet.name ?? ""] || "currentColor"}
                          className={cn(
                            "transition-all",
                            isPlanetSelected ? "stroke-foreground stroke-2" : "stroke-background"
                          )}
                          strokeWidth={2}
                        />
                        <text
                          y={4}
                          textAnchor="middle"
                          className="text-[10px] font-bold fill-white pointer-events-none"
                        >
                          {PLANET_SYMBOLS[planet.name ?? ""]}
                        </text>
                        {planet.retrograde && (
                          <text
                            y={-14}
                            textAnchor="middle"
                            className="text-[8px] fill-muted-foreground"
                          >
                            R
                          </text>
                        )}
                      </g>
                    );
                  })}
                </g>
              )}
            </g>
          );
        })
      )}
    </svg>
  );
}
