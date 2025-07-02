import React, { useEffect, useState } from "react";

function Companies() {
  const [companies, setCompanies] = useState([]);
  const [selectedSymbol, setSelectedSymbol] = useState("");
  const [details, setDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [error, setError] = useState("");
  const [reportLoading, setReportLoading] = useState(false);
  const [reportError, setReportError] = useState("");

  useEffect(() => {
    fetch("http://localhost:8000/api/companies/dropdown")
      .then((res) => res.json())
      .then((data) => {
        setCompanies(data);
        setLoading(false);
      });
  }, []);

  const handleSelect = (e) => {
    setSelectedSymbol(e.target.value);
    setDetails(null);
    setError("");
    setReportError("");
  };

  const handleShowDetails = () => {
    if (!selectedSymbol) {
      setError("Please select a company.");
      return;
    }
    setDetailsLoading(true);
    setError("");
    fetch(`http://localhost:8000/api/companies/${encodeURIComponent(selectedSymbol)}`)
      .then((res) => {
        if (!res.ok) throw new Error("Not found");
        return res.json();
      })
      .then((data) => {
        setDetails(data);
        setDetailsLoading(false);
      })
      .catch(() => {
        setError("Company details not found.");
        setDetailsLoading(false);
      });
  };

  const handleFetchAnnualReport = () => {
    if (!selectedSymbol) {
      setReportError("Please select a company.");
      return;
    }
    setReportLoading(true);
    setReportError("");
    fetch(`http://localhost:8000/api/companies/${encodeURIComponent(selectedSymbol)}/annual_report`)
      .then((res) => {
        if (!res.ok) throw new Error("Not found");
        return res.json();
      })
      .then((data) => {
        setReportLoading(false);
        if (data.view_url) {
          window.open(`http://localhost:8000${data.view_url}`, "_blank");
        } else {
          setReportError("Annual report not found.");
        }
      })
      .catch(() => {
        setReportError("Failed to fetch annual report.");
        setReportLoading(false);
      });
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h2>BSE Company Details Viewer</h2>
      <label htmlFor="companyDropdown">Select a company: </label>
      <select id="companyDropdown" value={selectedSymbol} onChange={handleSelect}>
        <option value="">-- Select --</option>
        {companies.map((company) => (
          <option key={company.symbol} value={company.symbol}>
            {company.symbol} - {company.name}
          </option>
        ))}
      </select>
      <button onClick={handleShowDetails} style={{ marginLeft: 8 }}>Show Details</button>
      <button onClick={handleFetchAnnualReport} style={{ marginLeft: 8 }}>View Annual Report</button>
      {detailsLoading && <div>Loading details...</div>}
      {error && <div style={{ color: "red" }}>{error}</div>}
      {reportLoading && <div>Fetching annual report...</div>}
      {reportError && <div style={{ color: "red" }}>{reportError}</div>}
      {details && (
        <table border="1" cellPadding="5" style={{ marginTop: 16 }}>
          <tbody>
            {Object.entries(details).map(([key, value]) => (
              <tr key={key}>
                <th>{key}</th>
                <td>{value !== null ? value.toString() : ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default Companies; 