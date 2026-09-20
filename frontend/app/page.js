"use client";

import { useState } from "react";

// Main component
export default function Home() {
  const [domain, setDomain] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Scan function
  const handleScan = async () => {
    if (!domain.trim()) {
      setError("Please enter a domain.");
      return;
    }

    try {
      setError("");
      setResults([]);
      setLoading(true);

      // FastAPI backend-এর scan API call
      const response = await fetch(
        `http://127.0.0.1:8000/scan?domains=${encodeURIComponent(domain)}`,
      );

      // Backend error হলে
      if (!response.ok) {
        throw new Error("Backend request failed.");
      }

      // Backend থেকে JSON data নেওয়া
      const data = await response.json();

      console.log("Backend response:", data);

      // Backend-এর results frontend state-এ রাখা
      setResults(data.results);
    } catch (error) {
      console.error("Backend error:", error);

      setError(
        "Could not connect to the backend. Please make sure the FastAPI server is running.",
      );
    } finally {
      // Scan শেষ হলে loading বন্ধ
      setLoading(false);
    }
  };

  // JSON Download
  const handleJsonDownload = async () => {
    try {
      // Backend-এর JSON download API call
      const response = await fetch("http://127.0.0.1:8000/download/json");

      // Download error হলে
      if (!response.ok) {
        throw new Error("JSON download failed.");
      }

      // Response-কে file/blob হিসেবে নেওয়া
      const blob = await response.blob();

      // Temporary browser URL তৈরি
      const url = window.URL.createObjectURL(blob);

      // Download link তৈরি
      const link = document.createElement("a");

      link.href = url;
      link.download = "results.json";

      // Download শুরু
      link.click();

      // Temporary URL remove
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("JSON download error:", error);

      setError("Could not download JSON file.");
    }
  };

  // CSV Download
  const handleCsvDownload = async () => {
    try {
      // Backend-এর CSV download API call
      const response = await fetch("http://127.0.0.1:8000/download/csv");

      // Download error হলে
      if (!response.ok) {
        throw new Error("CSV download failed.");
      }

      // Response-কে file/blob হিসেবে নেওয়া
      const blob = await response.blob();

      // Temporary browser URL তৈরি
      const url = window.URL.createObjectURL(blob);

      // Download link তৈরি
      const link = document.createElement("a");

      link.href = url;
      link.download = "results.csv";

      // Download শুরু
      link.click();

      // Temporary URL remove
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("CSV download error:", error);

      setError("Could not download CSV file.");
    }
  };

  // Total subdomain count
  const totalSubdomains = results.reduce(
    (total, item) => total + item.subdomains.length,
    0,
  );

  // Valid count // live === true
  const validCount = results.reduce(
    (total, item) =>
      total +
      item.subdomains.filter((subdomain) => subdomain.live === true).length,
    0,
  );

  // Failed count // live === false
  const failedCount = results.reduce(
    (total, item) =>
      total +
      item.subdomains.filter((subdomain) => subdomain.live === false).length,
    0,
  );

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <header className="border-b border-slate-800 text-center bg-slate-950/95">
        <div className="mx-auto max-w-6xl px-6 py-6">
          <h1 className="text-2xl font-bold tracking-tight">
            Subdomain Finder
          </h1>

          <p className="mt-1 text-sm text-slate-400">
            Discover and validate authorized domains
          </p>
        </div>
      </header>

      <div className="mx-auto max-w-6xl px-6 py-10">
        <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
          <div className="mb-5">
            <h2 className="text-xl font-semibold">Scan a Domain</h2>

            <p className="mt-1 text-sm text-slate-400">
              Enter one or more authorized domains. Use commas to separate
              multiple domains.
            </p>
          </div>

          <div className="flex flex-col gap-3 sm:flex-row">
            <input
              type="text"
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  handleScan();
                }
              }}
              placeholder="Search domains..."
              disabled={loading}
              className="flex-1 rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 disabled:cursor-not-allowed disabled:opacity-50"
            />

            <button
              onClick={handleScan}
              disabled={loading}
              className="cursor-pointer rounded-xl bg-blue-500 px-8 py-3 font-semibold transition hover:bg-blue-600 active:scale-95 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Scanning..." : "Scan Domain"}
            </button>
          </div>

          {/* Loading */}
          {loading && (
            <div className="mt-4 rounded-xl border border-blue-900 bg-blue-950/40 px-4 py-3 text-sm text-blue-300">
              Scanning... Please wait while subdomains are being discovered.
            </div>
          )}

          {/* Error */}
          {error && !loading && (
            <div className="mt-4 rounded-xl border border-red-900 bg-red-950/40 px-4 py-3 text-sm text-red-300">
              {error}
            </div>
          )}
        </section>

        {/* Statistics */}
        <section className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
          {/* Total */}
          <div className="rounded-2xl text-center border border-slate-800 bg-slate-900 p-6">
            <p className="text-sm">Subdomains Found</p>

            <p className="mt-3 text-4xl font-bold">{totalSubdomains}</p>
          </div>

          {/* Valid */}
          <div className="rounded-2xl text-center border border-slate-800 bg-slate-900 p-6">
            <p className="text-sm text-slate-400">Valid</p>

            <p className="mt-3 text-4xl font-bold text-green-400">
              {validCount}
            </p>

            <p className="mt-1 text-xs text-slate-500">
              DNS + HTTP/HTTPS available
            </p>
          </div>

          {/* Failed */}
          <div className="rounded-2xl border text-center border-slate-800 bg-slate-900 p-6">
            <p className="text-sm text-slate-400">Failed</p>

            <p className="mt-3 text-4xl text-center font-bold text-red-400">
              {failedCount}
            </p>

            <p className="mt-1 text-xs text-slate-500">Not live</p>
          </div>
        </section>

        {/* Results Section */}
        <section className="mt-6 overflow-hidden rounded-2xl border border-slate-800 bg-slate-900">
          {/* Results header */}
          <div className="flex flex-col gap-4 border-b border-slate-800 px-6 py-5 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-xl font-semibold">Scan Results</h2>

              <p className="mt-1 text-sm text-slate-400">
                Discovered subdomains will appear here.
              </p>
            </div>

            {/* Download buttons */}
            <div className="flex gap-2">
              <button
                onClick={handleJsonDownload}
                disabled={results.length === 0 || loading}
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-40"
              >
                JSON
              </button>

              <button
                onClick={handleCsvDownload}
                disabled={results.length === 0 || loading}
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-40"
              >
                CSV
              </button>
            </div>
          </div>

          {/* Results Table */}
          {results.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-center">
                <thead className="border-b border-slate-800 bg-slate-950">
                  <tr>
                    <th className="px-6 py-4 text-sm font-semibold text-slate-300">
                      Domain
                    </th>

                    <th className="px-6 py-4 text-sm font-semibold text-slate-300">
                      Subdomain
                    </th>

                    <th className="px-6 py-4 text-sm font-semibold text-slate-300">
                      DNS
                    </th>

                    <th className="px-6 py-4 text-sm font-semibold text-slate-300">
                      HTTP/HTTPS
                    </th>

                    <th className="px-6 py-4 text-sm font-semibold text-slate-300">
                      Status
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {results.map((item, index) =>
                    item.subdomains.map((subdomain, subIndex) => (
                      <tr
                        key={`${index}-${subIndex}`}
                        className="border-b border-slate-800 transition hover:bg-slate-800/50"
                      >
                        <td className="px-6 py-4 text-sm text-slate-400">
                          {item.domain}
                        </td>

                        <td className="px-6 py-4 text-sm text-blue-400">
                          {subdomain.subdomain}
                        </td>

                        <td className="px-6 py-4 text-sm">
                          {subdomain.dns_valid ? (
                            <span className="text-green-400">Valid</span>
                          ) : (
                            <span className="text-red-400">Failed</span>
                          )}
                        </td>

                        <td className="px-10 py-4 text-sm">
                          {subdomain.http_valid ? (
                            <span className="text-green-400">Valid</span>
                          ) : (
                            <span className="text-red-400">Failed</span>
                          )}
                        </td>

                        <td className="px-3 py-4 text-sm">
                          {subdomain.live ? (
                            <span className="rounded-full bg-green-500/10 px-3 py-1 text-xs font-semibold text-green-400">
                              LIVE
                            </span>
                          ) : (
                            <span className="rounded-full bg-red-500/10 px-3 py-1 text-xs font-semibold text-red-400">
                              FAILED
                            </span>
                          )}
                        </td>
                      </tr>
                    )),
                  )}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="px-6 py-16 text-center">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-slate-800 text-2xl">
                🔍
              </div>

              <h3 className="mt-4 text-lg font-semibold">
                {loading ? "Scanning..." : "No results yet"}
              </h3>

              <p className="mt-2 text-sm text-slate-500">
                {loading
                  ? "Please wait for the scan to finish."
                  : "Enter a domain above and start a scan."}
              </p>
            </div>
          )}
        </section>

        <footer className="py-8 text-center text-sm text-slate-500">
          Subdomain Finder • Authorized Security Testing
        </footer>
      </div>
    </main>
  );
}
