import { useMemo, useState } from "react";
import { useEffect } from "react";
import AttackGraph from "./components/AttackGraph";

export default function Dashboard() {
  const [logs, setLogs] = useState("");
  const [output, setOutput] = useState(null);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");
  const [riskFilter, setRiskFilter] = useState("ALL");
  const [stats, setStats] = useState(null);


  
  const fetchStats = async () => {
  try {
    const res = await fetch("http://127.0.0.1:8000/api/stats");
    const data = await res.json();

    setStats(data);
  } catch (err) {
    console.error(err);
  }
};
  const ingestLogs = async () => {
    try {
      setLoading(true);

      const parsed = JSON.parse(logs);

      const res = await fetch("http://127.0.0.1:8000/api/ingest", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(parsed),
      });

      const data = await res.json();

      alert(data.message || "Logs ingested successfully");
    } catch (err) {
      console.error(err);
      alert("Invalid JSON logs");
    } finally {
      setLoading(false);
    }
  };

  const runPrediction = async () => {
    try {
      setLoading(true);

      const res = await fetch("http://127.0.0.1:8000/api/predict", {
        method: "POST",
      });

      const data = await res.json();

      console.log(data);
      setOutput(data);
    } catch (err) {
      console.error(err);
      alert("Prediction failed");
    } finally {
      setLoading(false);
    }
  };

  const exportCSV = () => {
    window.open("http://127.0.0.1:8000/api/export/csv", "_blank");
  };

  const exportPDF = () => {
    window.open("http://127.0.0.1:8000/api/export/pdf", "_blank");
  };

  const filteredAnomalies = useMemo(() => {
    if (!output?.anomalies) return [];

    return output.anomalies.filter((a) => {
      const matchesSearch =
        !search ||
        a.user?.toLowerCase().includes(search.toLowerCase());

      let risk = "LOW";

      if ((a.probability || 0) >= 0.8) risk = "HIGH";
      else if ((a.probability || 0) >= 0.5) risk = "MEDIUM";

      const matchesRisk =
        riskFilter === "ALL" || risk === riskFilter;

      return matchesSearch && matchesRisk;
    });
  }, [output, search, riskFilter]);

  const getRisk = (p) => {
    if (p >= 0.8) return "HIGH";
    if (p >= 0.5) return "MEDIUM";
    return "LOW";
  };

  const getRiskColor = (risk) => {
    if (risk === "HIGH") {
      return "bg-red-500/20 text-red-300 border border-red-500/30";
    }

    if (risk === "MEDIUM") {
      return "bg-yellow-500/20 text-yellow-300 border border-yellow-500/30";
    }

    return "bg-green-500/20 text-green-300 border border-green-500/30";
  };


  const resetSystem = async () => {
    try {
      setLoading(true);

      const res = await fetch(
        "http://127.0.0.1:8000/api/reset",
        {
          method: "POST",
        }
      );

      const data = await res.json();

      console.log(data);

      setOutput(null);
      setStats(null);

      alert("System reset successful");
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();  
    const interval = setInterval(fetchStats, 15000);

    return () => clearInterval(interval);
  }, []);


  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-slate-950 to-slate-900 text-white p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="bg-white/5 border border-white/10 rounded-3xl p-8 backdrop-blur-sm shadow-2xl">
          <h1 className="text-5xl font-bold tracking-tight">
            AI-Powered Cyber Forensics Dashboard
            
          </h1>
           <AttackGraph />
          <p className="text-slate-300 mt-4 text-lg max-w-3xl">
            Behavioral anomaly detection, forensic timeline reconstruction,
            explainable AI inference, and automated cyber investigation
            reporting.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white/5 border border-white/10 rounded-2xl p-6 shadow-xl">
            <p className="text-slate-400 text-sm">Total Logs</p>
            <h2 className="text-4xl font-bold mt-2">
              {stats?.total_logs || 0}
            </h2>
          </div>

          <div className="bg-white/5 border border-white/10 rounded-2xl p-6 shadow-xl">
            <p className="text-slate-400 text-sm">Detected Anomalies</p>
            <h2 className="text-4xl font-bold mt-2 text-red-300">
               {stats?.total_anomalies || 0}
            </h2>
          </div>

          <div className="bg-white/5 border border-white/10 rounded-2xl p-6 shadow-xl">
            <p className="text-slate-400 text-sm">High Risk Events</p>
            <h2 className="text-4xl font-bold mt-2 text-yellow-300">
               {stats?.high_risk_events || 0}
            </h2>
          </div>

          <div className="bg-white/5 border border-white/10 rounded-2xl p-6 shadow-xl">
            <p className="text-slate-400 text-sm">Users Investigated</p>
            <h2 className="text-4xl font-bold mt-2 text-cyan-300">
              {stats?.users_investigated || 0}
            </h2>
          </div>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <div className="bg-white/5 border border-white/10 rounded-3xl p-6 shadow-xl">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-2xl font-semibold">Log Ingestion</h2>

              <div className="text-sm text-slate-400">
                JSON Event Input
              </div>
            </div>

            <textarea
              value={logs}
              onChange={(e) => setLogs(e.target.value)}
              className="w-full h-72 rounded-2xl bg-black/40 border border-white/10 p-4 font-mono text-sm outline-none focus:border-cyan-400"
              placeholder="Paste logs JSON here..."
            />

            <div className="flex gap-3 mt-5">
              <button
                onClick={ingestLogs}
                disabled={loading}
                className="bg-cyan-500 hover:bg-cyan-400 transition px-6 py-3 rounded-2xl font-semibold text-black"
              >
                {loading ? "Processing..." : "Ingest Logs"}
              </button>

              <button
                onClick={() => setLogs("")}
                className="bg-white/10 hover:bg-white/20 transition px-6 py-3 rounded-2xl"
              >
                Clear
              </button>
            </div>
          </div>

          <div className="bg-white/5 border border-white/10 rounded-3xl p-6 shadow-xl">
            <h2 className="text-2xl font-semibold mb-6">
              ML Detection Controls
            </h2>

            <div className="grid grid-cols-1 gap-4">
              <button
                onClick={runPrediction}
                disabled={loading}
                className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:opacity-90 transition py-4 rounded-2xl text-lg font-semibold text-black"
              >
                {loading ? "Running..." : "Run ML Prediction"}
              </button>

              <button
                onClick={exportCSV}
                className="bg-white/10 hover:bg-white/20 transition py-4 rounded-2xl text-lg"
              >
                Export CSV Report
              </button>

              <button
                onClick={exportPDF}
                className="bg-white/10 hover:bg-white/20 transition py-4 rounded-2xl text-lg"
              >
                Export PDF Report
              </button>

              <button
                onClick={resetSystem}
                className="bg-red-500 hover:bg-red-400 transition py-4 rounded-2xl text-lg font-semibold text-black"
              >
                Reset System
              </button>
            </div>

            <div className="mt-8 bg-black/30 border border-white/10 rounded-2xl p-5">
              <h3 className="font-semibold text-lg mb-2">System Status</h3>

              <div className="space-y-2 text-sm text-slate-300">
                <p>• ML inference engine active</p>
                <p>• Rule engine calibration loaded</p>
                <p>• CERT behavioral baselines loaded</p>
                <p>• Feature alignment enabled</p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white/5 border border-white/10 rounded-3xl p-6 shadow-xl overflow-hidden">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-6">
            <h2 className="text-3xl font-semibold">Detected Anomalies</h2>

            <div className="flex flex-col md:flex-row gap-3">
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="bg-black/30 border border-white/10 rounded-xl px-4 py-3 outline-none focus:border-cyan-400"
                placeholder="Search user"
              />

              <select
                value={riskFilter}
                onChange={(e) => setRiskFilter(e.target.value)}
                className="bg-black/30 border border-white/10 rounded-xl px-4 py-3 outline-none focus:border-cyan-400"
              >
                <option value="ALL">All Risk Levels</option>
                <option value="HIGH">HIGH</option>
                <option value="MEDIUM">MEDIUM</option>
                <option value="LOW">LOW</option>
              </select>
            </div>
          </div>

          <div className="overflow-x-auto rounded-2xl border border-white/10">
            <table className="w-full text-sm">
              <thead className="bg-white/5 text-slate-300">
                <tr>
                  <th className="text-left px-6 py-4">User</th>
                  <th className="text-left px-6 py-4">Probability</th>
                  <th className="text-left px-6 py-4">Risk</th>
                  <th className="text-left px-6 py-4">Activity</th>
                  <th className="text-left px-6 py-4">Reasons</th>
                </tr>
              </thead>

              <tbody>
                {filteredAnomalies.length > 0 ? (
                  filteredAnomalies.map((a, idx) => {
                    const risk = getRisk(a.probability || 0);

                    return (
                      <tr
                        key={idx}
                        className="border-t border-white/10 hover:bg-white/5 transition"
                      >
                        <td className="px-6 py-5 font-medium">{a.user}</td>

                        <td className="px-6 py-5">
                          {(a.probability || 0).toFixed(2)}
                        </td>

                        <td className="px-6 py-5">
                          <span
                            className={`px-3 py-1 rounded-full text-xs font-semibold ${getRiskColor(
                              risk
                            )}`}
                          >
                            {risk}
                          </span>
                        </td>

                        <td className="px-6 py-5 text-slate-300">
                          Files: {a.file_count || 0} | Devices: {a.device_count || 0}
                        </td>

                        <td className="px-6 py-5 text-slate-300 max-w-md">
                          {a.reasons?.join(", ") ||
                            "Behavior deviation detected"}
                        </td>
                      </tr>
                    );
                  })
                ) : (
                  <tr>
                    <td
                      colSpan={5}
                      className="text-center py-10 text-slate-400"
                    >
                      No anomalies detected yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-white/5 border border-white/10 rounded-3xl p-6 shadow-xl">
          <h2 className="text-3xl font-semibold mb-8">
            Investigation Timeline
          </h2>

          <div className="space-y-8 border-l border-cyan-500/30 ml-3 pl-8">
            {filteredAnomalies.slice(0, 5).map((a, idx) => (
              <div key={idx} className="relative">
                <div className="absolute -left-[41px] top-2 w-4 h-4 rounded-full bg-cyan-400" />

                <p className="text-sm text-slate-400 mb-2">
                  Anomaly Probability: {(a.probability || 0).toFixed(2)}
                </p>

                <h3 className="text-xl font-semibold mb-2">
                  Suspicious Activity Detected for {a.user}
                </h3>

                <p className="text-slate-300">
                  {a.reasons?.join(", ") ||
                    "Behavior deviation detected"}
                </p>
               
              </div>
              
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
