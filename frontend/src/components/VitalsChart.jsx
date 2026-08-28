// Line chart of a patient's vitals over time, built with Recharts.

import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from "recharts";

export default function VitalsChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={240}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
        <XAxis dataKey="timestamp" stroke="#94a3b8" />
        <YAxis stroke="#94a3b8" />
        <Tooltip />
        <Line type="monotone" dataKey="heart_rate" stroke="#f87171" dot={false} />
        <Line type="monotone" dataKey="lactate" stroke="#facc15" dot={false} />
        <Line type="monotone" dataKey="respiratory_rate" stroke="#38bdf8" dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
