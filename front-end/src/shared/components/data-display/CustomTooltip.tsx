interface TooltipPayloadItem {
  name: string;
  value: string | number;
  color?: string;
  dataKey?: string | number;
  payload?: Record<string, any>;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: TooltipPayloadItem[];
  label?: string | number;
  labelPrefix?: string;
  valueFormatter?: (value: string | number) => string;
}

export const CustomTooltip = ({ active, payload, label, labelPrefix = "", valueFormatter }: CustomTooltipProps) => {
  if (active && payload?.length) {
    return (
      <div className="bg-card border border-border rounded-lg p-3 shadow-lg text-xs" dir="rtl">
        <p className="font-semibold text-foreground mb-1">
          {labelPrefix}{label}
        </p>
        {payload.map((p) => (
          <p key={p.name || p.dataKey} style={{ color: p.color }}>
            {p.name}: {valueFormatter ? valueFormatter(p.value) : (typeof p.value === 'number' ? p.value.toFixed(2) : p.value)}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export default CustomTooltip;
