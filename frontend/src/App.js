import { useState, useEffect } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

const API = "";

function App() {
  const [reports, setReports] = useState([]);
  const [selected, setSelected] = useState(null);
  const [report, setReport] = useState(null);

  useEffect(() => {
    fetch(`${API}/api/reports`)
      .then(r => r.json())
      .then(data => {
        const seen = new Set();
        const unique = data.filter(r => {
          const parts = r.replace(".json", "").split("_");
          const key = parts.slice(0, -2).join("_");
          if (seen.has(key)) return false;
          seen.add(key);
          return true;
        });
        setReports(unique);
        if (unique.length > 0) {
          const latest = unique[unique.length - 1];
          setSelected(latest);
          fetch(`${API}/api/reports/${latest}`)
            .then(r => r.json())
            .then(d => setReport(d));
        }
      });
  }, []);

  function loadReport(filename) {
    setSelected(filename);
    fetch(`${API}/api/reports/${filename}`)
      .then(r => r.json())
      .then(data => setReport(data));
  }

  function formatMarket(market) {
    if (!market) return "";
    return market.replace(/_/g, " ").toLowerCase();
  }

  function clockLabel(seconds) {
    if (!seconds) return "unknown";
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${String(s).padStart(2, "0")}`;
  }

  const chartData = report
    ? report.top_20_shifts.map((s, i) => ({
        name: `${s.time_readable}`,
        shift: s.abs_shift,
        direction: s.shift > 0 ? "up" : "down",
        market: formatMarket(s.market),
        label: s.label,
        from: s.from_odds,
        to: s.to_odds,
        event_gap: s.nearest_event_gap_seconds,
        clock: s.nearest_event ? clockLabel(s.nearest_event.clock_seconds) : "none"
      }))
    : [];

  return (
    <div style={{ fontFamily: "sans-serif", background: "#0f1117", minHeight: "100vh", color: "#e0e0e0", display: "flex" }}>
      <div style={{ width: 280, background: "#1a1d27", padding: 20, borderRight: "1px solid #2a2d3a" }}>
        <div style={{ fontSize: 20, fontWeight: 700, color: "#fff", marginBottom: 4 }}>Odds Autopsy</div>
        <div style={{ fontSize: 12, color: "#888", marginBottom: 24 }}>World Cup forensic reports</div>
        {reports.map(r => {
          const parts = r.replace(".json", "").split("_");
          const label = parts.slice(0, -3).join(" ");
          return (
            <div
              key={r}
              onClick={() => loadReport(r)}
              style={{
                padding: "10px 14px",
                marginBottom: 8,
                borderRadius: 8,
                cursor: "pointer",
                background: selected === r ? "#2a2d3a" : "transparent",
                border: selected === r ? "1px solid #4a9eff" : "1px solid transparent",
                fontSize: 13,
                color: selected === r ? "#4a9eff" : "#ccc"
              }}
            >
              {label}
            </div>
          );
        })}
      </div>

      <div style={{ flex: 1, padding: 32 }}>
        {!report && (
          <div style={{ color: "#555", marginTop: 80, textAlign: "center", fontSize: 16 }}>
            Select a match from the left to view its autopsy report
          </div>
        )}

        {report && (
          <>
            <div style={{ fontSize: 24, fontWeight: 700, color: "#fff", marginBottom: 4 }}>
              {report.fixture.name}
            </div>
            <div style={{ fontSize: 13, color: "#888", marginBottom: 8 }}>
              {report.fixture.competition} - {report.total_odds_updates} odds updates - {report.total_shifts_detected} shifts detected
            </div>
            {report.solana && (
              <a
                href={`https://solscan.io/tx/${report.solana.signature}`}
                target="_blank"
                rel="noreferrer"
                style={{ fontSize: 12, color: "#50fa7b", textDecoration: "none", display: "inline-block", marginBottom: 24, background: "#1a2a1a", padding: "4px 12px", borderRadius: 6, border: "1px solid #50fa7b33" }}
              >
                anchored on solana - {report.solana.hash.slice(0, 16)}... view on solscan
              </a>
            )}

            <div style={{ display: "flex", gap: 16, marginBottom: 32 }}>
              {[
                { label: "Odds Updates", value: report.total_odds_updates },
                { label: "Shifts Found", value: report.total_shifts_detected },
                { label: "Score Events", value: report.total_score_updates },
                { label: "Top Shift", value: report.top_20_shifts[0]?.abs_shift.toFixed(3) }
              ].map(card => (
                <div key={card.label} style={{ background: "#1a1d27", borderRadius: 10, padding: "16px 24px", flex: 1, border: "1px solid #2a2d3a" }}>
                  <div style={{ fontSize: 12, color: "#888", marginBottom: 6 }}>{card.label}</div>
                  <div style={{ fontSize: 26, fontWeight: 700, color: "#4a9eff" }}>{card.value}</div>
                </div>
              ))}
            </div>

            <div style={{ background: "#1a1d27", borderRadius: 10, padding: 24, marginBottom: 32, border: "1px solid #2a2d3a" }}>
              <div style={{ fontSize: 15, fontWeight: 600, marginBottom: 16, color: "#fff" }}>Top 20 Odds Shifts</div>
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={chartData} margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
                  <XAxis dataKey="name" tick={{ fontSize: 10, fill: "#666" }} />
                  <YAxis tick={{ fontSize: 10, fill: "#666" }} />
                  <Tooltip
                    contentStyle={{ background: "#1a1d27", border: "1px solid #2a2d3a", borderRadius: 8, fontSize: 12 }}
                    formatter={(value, name, props) => [
                      `${value} (${props.payload.market} - ${props.payload.label})`,
                      "Shift size"
                    ]}
                  />
                  <Bar dataKey="shift" radius={[4, 4, 0, 0]}>
                    {chartData.map((entry, i) => (
                      <Cell key={i} fill={entry.direction === "up" ? "#4a9eff" : "#ff6b6b"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div style={{ background: "#1a1d27", borderRadius: 10, padding: 24, border: "1px solid #2a2d3a" }}>
              <div style={{ fontSize: 15, fontWeight: 600, marginBottom: 16, color: "#fff" }}>Shift Details</div>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
                <thead>
                  <tr style={{ color: "#888", borderBottom: "1px solid #2a2d3a" }}>
                    <th style={{ textAlign: "left", padding: "8px 12px" }}>Time</th>
                    <th style={{ textAlign: "left", padding: "8px 12px" }}>Market</th>
                    <th style={{ textAlign: "left", padding: "8px 12px" }}>Selection</th>
                    <th style={{ textAlign: "right", padding: "8px 12px" }}>From</th>
                    <th style={{ textAlign: "right", padding: "8px 12px" }}>To</th>
                    <th style={{ textAlign: "right", padding: "8px 12px" }}>Shift</th>
                    <th style={{ textAlign: "right", padding: "8px 12px" }}>Match Clock</th>
                    <th style={{ textAlign: "right", padding: "8px 12px" }}>Event Gap</th>
                  </tr>
                </thead>
                <tbody>
                  {report.top_20_shifts.map((s, i) => (
                    <tr key={i} style={{ borderBottom: "1px solid #1e2130", color: i % 2 === 0 ? "#ccc" : "#bbb" }}>
                      <td style={{ padding: "8px 12px" }}>{s.time_readable}</td>
                      <td style={{ padding: "8px 12px" }}>{formatMarket(s.market)}</td>
                      <td style={{ padding: "8px 12px" }}>{s.label}</td>
                      <td style={{ padding: "8px 12px", textAlign: "right" }}>{s.from_odds}</td>
                      <td style={{ padding: "8px 12px", textAlign: "right" }}>{s.to_odds}</td>
                      <td style={{ padding: "8px 12px", textAlign: "right", color: s.shift > 0 ? "#4a9eff" : "#ff6b6b", fontWeight: 600 }}>
                        {s.shift > 0 ? "+" : ""}{s.shift}
                      </td>
                      <td style={{ padding: "8px 12px", textAlign: "right" }}>
                        {s.nearest_event ? clockLabel(s.nearest_event.clock_seconds) : "none"}
                      </td>
                      <td style={{ padding: "8px 12px", textAlign: "right", color: s.nearest_event_gap_seconds < 10 ? "#50fa7b" : "#888" }}>
                        {s.nearest_event_gap_seconds === null ? "none" : `${s.nearest_event_gap_seconds}s`}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default App;