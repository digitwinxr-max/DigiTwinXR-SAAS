import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

function MeasurementChart({ data, unit }) {
  if (!data || data.length === 0) {
    return <div className="no-data">No measurements to display</div>;
  }

  const formatXAxis = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="chart-tooltip">
          <p>{new Date(payload[0].payload.timestamp).toLocaleString()}</p>
          <p>
            <strong>Value:</strong> {payload[0].value} {unit || ''}
          </p>
          <p>
            <strong>Quality:</strong> {payload[0].payload.quality}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="measurement-chart">
      <ResponsiveContainer width="100%" height={400}>
        <LineChart
          data={data}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="timestamp"
            tickFormatter={formatXAxis}
            interval="preserveStartEnd"
          />
          <YAxis
            tickFormatter={(value) => `${value}${unit ? ` ${unit}` : ''}`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Line
            type="monotone"
            dataKey="value"
            stroke="#2563eb"
            strokeWidth={2}
            dot={{ r: 3 }}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default MeasurementChart;
