"use client";

import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid } from "recharts";
import { pathwayData } from "@/lib/studio-data";

export function EnergyDiagram() {
  return (
    <div className="h-72 w-full">
      <ResponsiveContainer>
        <LineChart data={pathwayData} margin={{ left: 0, right: 8, top: 12, bottom: 0 }}>
          <CartesianGrid stroke="hsl(var(--studio-line))" strokeOpacity={0.35} vertical={false} />
          <XAxis dataKey="coordinate" tick={{ fill: "hsl(var(--studio-muted))", fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fill: "hsl(var(--studio-muted))", fontSize: 11 }} axisLine={false} tickLine={false} unit=" kcal" />
          <Tooltip
            contentStyle={{
              background: "hsl(var(--studio-panel))",
              border: "1px solid hsl(var(--studio-line))",
              borderRadius: 18,
              color: "hsl(var(--studio-text))"
            }}
          />
          <Line type="monotone" dataKey="DCS" stroke="hsl(var(--studio-cyan))" strokeWidth={3} dot={{ r: 4 }} />
          <Line type="monotone" dataKey="MCSOMe" stroke="hsl(var(--studio-violet))" strokeWidth={3} dot={{ r: 4 }} />
          <Line type="monotone" dataKey="DMOS" stroke="hsl(var(--studio-orange))" strokeWidth={3} dot={{ r: 4 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

