"use client";

import * as React from "react";
import * as RechartsPrimitive from "recharts";

import { cn } from "@/lib/utils";

export type ChartConfig = {
  [k: string]: {
    label?: React.ReactNode;
    color?: string;
  };
};

const ChartContext = React.createContext<{ config: ChartConfig } | null>(null);

function useChart() {
  const context = React.useContext(ChartContext);
  if (!context) {
    throw new Error("useChart must be used within a <ChartContainer />");
  }
  return context;
}

function ChartContainer({
  id,
  className,
  children,
  config,
  ...props
}: React.ComponentProps<"div"> & {
  config: ChartConfig;
  children: React.ComponentProps<typeof RechartsPrimitive.ResponsiveContainer>["children"];
}) {
  const uniqueId = React.useId();
  const chartId = `chart-${id ?? uniqueId.replace(/:/g, "")}`;

  const style = Object.entries(config).reduce((acc, [key, value]) => {
    if (value.color) {
      (acc as Record<string, string>)[`--color-${key}`] = value.color;
    }
    return acc;
  }, {} as React.CSSProperties);

  return (
    <ChartContext.Provider value={{ config }}>
      <div
        data-slot="chart"
        data-chart={chartId}
        style={style}
        className={cn("flex w-full items-center justify-center text-xs", className)}
        {...props}
      >
        <RechartsPrimitive.ResponsiveContainer>{children}</RechartsPrimitive.ResponsiveContainer>
      </div>
    </ChartContext.Provider>
  );
}

function ChartTooltipContent({
  active,
  payload,
  label,
  className,
}: React.ComponentProps<typeof RechartsPrimitive.Tooltip> & {
  className?: string;
}) {
  const { config } = useChart();

  if (!active || !payload?.length) {
    return null;
  }

  return (
    <div
      className={cn(
        "rounded-md border border-slate-300 bg-white px-3 py-2 shadow-sm",
        className,
      )}
    >
      {label ? (
        <p className="mb-1 text-xs font-medium text-slate-700 [font-family:var(--font-ibm-plex-mono)]">
          {String(label)}
        </p>
      ) : null}
      <div className="space-y-1">
        {payload.map((item) => {
          const key = String(item.dataKey ?? "value");
          const itemConfig = config[key];
          const color = item.color || item.payload.fill || "currentColor";
          return (
            <div key={key} className="flex items-center justify-between gap-3 text-xs">
              <div className="flex items-center gap-2">
                <span
                  className="h-2.5 w-2.5 rounded-sm"
                  style={{ backgroundColor: color }}
                />
                <span>{itemConfig?.label ?? key}</span>
              </div>
              <span className="font-medium tabular-nums">
                {typeof item.value === "number" ? item.value.toFixed(1) : String(item.value)}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

const ChartTooltip = RechartsPrimitive.Tooltip;

export { ChartContainer, ChartTooltip, ChartTooltipContent };
