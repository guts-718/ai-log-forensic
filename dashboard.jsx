


import { useState } from "react";

export default function Dashboard() {
  const [output, setOutput] = useState(null);
  const [logs, setLogs] = useState("");


  const runPrediction = async () => {
  try {
    const res = await fetch("http://127.0.0.1:8000/api/predict", {
      method: "POST",
    });

    const data = await res.json();

    console.log(data);

    setOutput(data);
  } catch (err) {
    console.error(err);
  }
};


const ingestLogs = async () => {
  try {
    const parsed = JSON.parse(logs);

    const res = await fetch("http://127.0.0.1:8000/api/ingest", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(parsed),
    });

    const data = await res.json();

    console.log(data);

    alert("Logs ingested!");
  } catch (err) {
    console.error(err);
    alert("Invalid JSON");
  }
};

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-7xl mx-auto space-y-6">

        <div className="bg-white rounded-3xl shadow p-6">
          <h1 className="text-4xl font-bold mb-2">AI-Powered Cyber Forensics Dashboard</h1>
          <p className="text-gray-600">
            Behavioral anomaly detection, forensic timeline reconstruction, and automated reporting.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-2xl shadow p-5">
            <p className="text-sm text-gray-500">Total Logs</p>
            <h2 className="text-3xl font-bold mt-2">18,432</h2>
          </div>

          <div className="bg-white rounded-2xl shadow p-5">
            <p className="text-sm text-gray-500">Detected Anomalies</p>
            <h2 className="text-3xl font-bold mt-2">243</h2>
          </div>

          <div className="bg-white rounded-2xl shadow p-5">
            <p className="text-sm text-gray-500">High Risk Events</p>
            <h2 className="text-3xl font-bold mt-2">51</h2>
          </div>

          <div className="bg-white rounded-2xl shadow p-5">
            <p className="text-sm text-gray-500">Users Investigated</p>
            <h2 className="text-3xl font-bold mt-2">76</h2>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

          <div className="bg-white rounded-3xl shadow p-6">
            <h2 className="text-2xl font-semibold mb-4">Log Ingestion</h2>

           <textarea
            value={logs}
            onChange={(e) => setLogs(e.target.value)}
            className="w-full h-64 border rounded-2xl p-4 font-mono text-sm"
            placeholder="Paste logs JSON here..."
          />

            <div className="flex gap-3 mt-4">
             <button
              onClick={ingestLogs}
              className="bg-black text-white px-5 py-3 rounded-2xl"
            >
              Ingest Logs
            </button>

              <button className="border px-5 py-3 rounded-2xl">
                Clear
              </button>
            </div>
          </div>

          <div className="bg-white rounded-3xl shadow p-6">
            <h2 className="text-2xl font-semibold mb-4">ML Detection Controls</h2>

            <div className="space-y-4">
              <button
                onClick={runPrediction}
                className="w-full bg-black text-white py-4 rounded-2xl text-lg font-medium"
              >
                Run ML Prediction
              </button>

              <button className="w-full border py-4 rounded-2xl text-lg font-medium">
                Generate Timeline
              </button>

              <button className="w-full border py-4 rounded-2xl text-lg font-medium">
                Export CSV Report
              </button>

              <button className="w-full border py-4 rounded-2xl text-lg font-medium">
                Export PDF Report
              </button>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-3xl shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-semibold">Detected Anomalies</h2>

            <div className="flex gap-3">
              <input
                className="border rounded-xl px-4 py-2"
                placeholder="Search user"
              />

              <select className="border rounded-xl px-4 py-2">
                <option>All Risk Levels</option>
                <option>HIGH</option>
                <option>MEDIUM</option>
                <option>LOW</option>
              </select>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b text-left text-gray-500">
                  <th className="py-3">User</th>
                  <th className="py-3">Probability</th>
                  <th className="py-3">Risk</th>
                  <th className="py-3">Activity</th>
                  <th className="py-3">Reason</th>
                </tr>
              </thead>

              <tbody>
                {output?.anomalies?.map((a, idx) => (
                  <tr key={idx} className="border-b">
                    <td className="py-4">{a.user}</td>

                    <td className="py-4">
                      {a.probability?.toFixed(2)}
                    </td>

                    <td className="py-4">
                      <span className="bg-red-100 text-red-700 px-3 py-1 rounded-full text-sm">
                        HIGH
                      </span>
                    </td>

                    <td className="py-4">
                      Files: {a.file_count} | Devices: {a.device_count}
                    </td>

                    <td className="py-4">
                      {a.reasons?.join(", ")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-white rounded-3xl shadow p-6">
          <h2 className="text-2xl font-semibold mb-6">Investigation Timeline</h2>

          <div className="space-y-5 border-l-2 border-gray-300 ml-3 pl-6">
            <div>
              <p className="text-sm text-gray-500">08:00 AM</p>
              <h3 className="font-semibold">User Logon</h3>
              <p className="text-gray-600">USR001 logged into PC-01</p>
            </div>

            <div>
              <p className="text-sm text-gray-500">08:05 AM</p>
              <h3 className="font-semibold">Confidential File Access</h3>
              <p className="text-gray-600">Multiple sensitive files accessed</p>
            </div>

            <div>
              <p className="text-sm text-gray-500">08:08 AM</p>
              <h3 className="font-semibold">USB Device Connected</h3>
              <p className="text-gray-600">Potential exfiltration attempt detected</p>
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}
