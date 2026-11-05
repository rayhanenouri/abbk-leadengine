import { useState, useEffect, useRef } from 'react';
import { Upload, FileText, RefreshCw, Trash2, Download, Check, X, Menu } from 'lucide-react';

const API_BASE_URL = `http://${window.location.hostname}:8000/api`;

export default function DatabaseImport({ onMenuClick }) {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);
  const [importing, setImporting] = useState(false);
  const [importHistory, setImportHistory] = useState([]);
  const [currentImport, setCurrentImport] = useState(null);
  const [progress, setProgress] = useState(0);
  const fileInputRef = useRef(null);

  useEffect(() => {
    fetchImportHistory();
  }, []);

  useEffect(() => {
    if (currentImport && currentImport.status !== 'completed' && currentImport.status !== 'failed') {
      const interval = setInterval(() => {
        fetchImportStatus(currentImport.id);
      }, 2000);
      return () => clearInterval(interval);
    }
  }, [currentImport]);

  const fetchImportHistory = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/imports/history`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setImportHistory(data);
      }
    } catch (error) {
      console.error('Error fetching import history:', error);
    }
  };

  const fetchImportStatus = async (importId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/imports/${importId}/status`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setCurrentImport(data);
        setProgress(data.progress);
        if (data.status === 'completed' || data.status === 'failed') {
          fetchImportHistory();
        }
      }
    } catch (error) {
      console.error('Error fetching import status:', error);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (selectedFile) => {
    const validExtensions = ['.csv', '.xlsx', '.xls'];
    const fileName = selectedFile.name.toLowerCase();
    const isValid = validExtensions.some(ext => fileName.endsWith(ext));

    if (!isValid) {
      alert('Invalid file type. Upload CSV or Excel files only.');
      return;
    }

    if (selectedFile.size > 10 * 1024 * 1024) {
      alert('File too large. Maximum 10MB.');
      return;
    }

    setFile(selectedFile);
  };

  const handleUploadAndProcess = async () => {
    if (!file) return;

    setImporting(true);
    setProgress(0);

    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('file', file);

      const uploadResponse = await fetch(`${API_BASE_URL}/imports/upload`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });

      if (!uploadResponse.ok) {
        const error = await uploadResponse.json();
        throw new Error(error.detail || 'Upload failed');
      }

      const uploadData = await uploadResponse.json();
      const importId = uploadData.import_id;
      setProgress(10);

      const processResponse = await fetch(`${API_BASE_URL}/imports/${importId}/process`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!processResponse.ok) {
        throw new Error('Processing failed');
      }

      setProgress(20);
      setCurrentImport({
        id: importId,
        filename: file.name,
        status: 'processing'
      });

      setFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }

    } catch (error) {
      console.error('Import error:', error);
      alert(`Import failed: ${error.message}`);
      setImporting(false);
      setProgress(0);
    }
  };

  const handleReprocess = async (importId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/imports/${importId}/reprocess`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        alert('Reprocessing started');
        fetchImportHistory();
      }
    } catch (error) {
      console.error('Reprocess error:', error);
      alert('Reprocessing failed');
    }
  };

  const handleDelete = async (importId) => {
    if (!confirm('Delete this import? (Leads will not be deleted)')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/imports/${importId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        fetchImportHistory();
      }
    } catch (error) {
      console.error('Delete error:', error);
      alert('Delete failed');
    }
  };

  const downloadTemplate = () => {
    const csvContent = `Company,Website,Phone,Sector,City,Country,LinkedIn,Email
ACME Engineering,www.acme.tn,+216 71 123 456,Manufacturing,Tunis,Tunisia,linkedin.com/company/acme,contact@acme.tn
Beta Design Bureau,www.beta-design.com.tn,+216 71 234 567,Engineering Services,Sfax,Tunisia,,info@beta-design.com.tn`;

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'import_template.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const getStatusBadge = (status) => {
    const styles = {
      pending: 'bg-neutral-100 text-neutral-600',
      processing: 'bg-blue-50 text-blue-700 border border-blue-200',
      completed: 'bg-emerald-50 text-emerald-700 border border-emerald-200',
      failed: 'bg-red-50 text-red-700 border border-red-200'
    };
    const labels = {
      pending: 'Pending',
      processing: 'Processing',
      completed: 'Completed',
      failed: 'Failed'
    };
    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${styles[status] || styles.pending}`}>
        {labels[status] || 'Pending'}
      </span>
    );
  };

  return (
    <div className="flex-1 bg-neutral-50">
      {/* Header */}
      <div className="bg-white border-b border-neutral-200">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={onMenuClick}
                className="md:hidden p-2 hover:bg-neutral-100 rounded-lg"
              >
                <Menu className="w-5 h-5 text-neutral-600" />
              </button>
              <div>
                <h1 className="text-xl font-semibold text-neutral-900">Database Import</h1>
                <p className="text-sm text-neutral-600 mt-0.5">Upload and enrich company databases</p>
              </div>
            </div>
            <button
              onClick={downloadTemplate}
              className="flex items-center gap-2 px-4 py-2 bg-white border border-neutral-300 rounded-lg text-sm font-medium text-neutral-700 hover:bg-neutral-50"
            >
              <Download className="w-4 h-4" />
              Template
            </button>
          </div>
        </div>
      </div>

      <div className="p-6 max-w-6xl mx-auto space-y-6">
        {/* Upload Section */}
        <div className="bg-white rounded-lg border border-neutral-200 p-6">
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`
              relative border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-all
              ${dragActive
                ? 'border-blue-500 bg-blue-50'
                : 'border-neutral-300 bg-neutral-50 hover:border-neutral-400 hover:bg-neutral-100'
              }
            `}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv,.xlsx,.xls"
              onChange={handleFileSelect}
              className="hidden"
            />

            <div className="space-y-3">
              <div className="flex justify-center">
                <div className="p-3 bg-neutral-100 rounded-lg">
                  <Upload className="w-8 h-8 text-neutral-600" />
                </div>
              </div>
              <div>
                <p className="text-base font-medium text-neutral-900">
                  {file ? file.name : 'Drop file here or click to browse'}
                </p>
                <p className="text-sm text-neutral-500 mt-1">
                  CSV or Excel files (max 10MB)
                </p>
              </div>
              {file && (
                <div className="inline-block bg-neutral-100 px-3 py-1.5 rounded-md">
                  <p className="text-sm font-medium text-neutral-700">
                    {(file.size / 1024).toFixed(1)} KB
                  </p>
                </div>
              )}
            </div>
          </div>

          {file && !importing && (
            <div className="mt-4 flex justify-end">
              <button
                onClick={handleUploadAndProcess}
                className="px-6 py-2.5 bg-neutral-900 text-white rounded-lg font-medium hover:bg-neutral-800 transition-colors"
              >
                Upload & Process
              </button>
            </div>
          )}

          {/* Processing Progress */}
          {currentImport && currentImport.status === 'processing' && (
            <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-5">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <p className="font-medium text-blue-900">{currentImport.filename}</p>
                  <p className="text-sm text-blue-700 mt-1">
                    {currentImport.enriched_count || 0} / {currentImport.total_rows} enriched
                  </p>
                </div>
                <span className="text-xl font-semibold text-blue-700">{progress}%</span>
              </div>

              <div className="w-full bg-blue-200 rounded-full h-2.5 overflow-hidden">
                <div
                  className="bg-blue-600 h-full transition-all duration-500"
                  style={{ width: `${progress}%` }}
                />
              </div>

              <div className="grid grid-cols-4 gap-3 mt-4 text-sm">
                <div>
                  <p className="text-blue-600">Imported</p>
                  <p className="text-blue-900 font-semibold">{currentImport.imported_count}</p>
                </div>
                <div>
                  <p className="text-blue-600">Updated</p>
                  <p className="text-blue-900 font-semibold">{currentImport.updated_count}</p>
                </div>
                <div>
                  <p className="text-blue-600">Duplicates</p>
                  <p className="text-blue-900 font-semibold">{currentImport.duplicates_count}</p>
                </div>
                <div>
                  <p className="text-blue-600">Signals</p>
                  <p className="text-blue-900 font-semibold">{currentImport.signals_count}</p>
                </div>
              </div>
            </div>
          )}

          {/* Completion */}
          {currentImport && currentImport.status === 'completed' && (
            <div className="mt-6 bg-emerald-50 border border-emerald-200 rounded-lg p-5">
              <div className="flex items-start gap-3">
                <div className="p-1.5 bg-emerald-100 rounded">
                  <Check className="w-5 h-5 text-emerald-700" />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-emerald-900 mb-3">Import Complete</p>
                  <div className="grid grid-cols-4 gap-3 text-sm">
                    <div>
                      <p className="text-emerald-700">New</p>
                      <p className="font-semibold text-emerald-900">{currentImport.imported_count}</p>
                    </div>
                    <div>
                      <p className="text-emerald-700">Updated</p>
                      <p className="font-semibold text-emerald-900">{currentImport.updated_count}</p>
                    </div>
                    <div>
                      <p className="text-emerald-700">Enriched</p>
                      <p className="font-semibold text-emerald-900">{currentImport.enriched_count}</p>
                    </div>
                    <div>
                      <p className="text-emerald-700">Signals</p>
                      <p className="font-semibold text-emerald-900">{currentImport.signals_count}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => setCurrentImport(null)}
                    className="mt-4 px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-medium hover:bg-emerald-700"
                  >
                    Import Another File
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Import History */}
        <div className="bg-white rounded-lg border border-neutral-200 p-6">
          <h2 className="text-base font-semibold text-neutral-900 mb-4">Import History</h2>

          {importHistory.length === 0 ? (
            <div className="text-center py-12 text-neutral-500">
              <FileText className="w-12 h-12 mx-auto mb-3 text-neutral-400" />
              <p>No imports yet</p>
            </div>
          ) : (
            <div className="space-y-3">
              {importHistory.map((imp) => (
                <div
                  key={imp.id}
                  className="border border-neutral-200 rounded-lg p-4 hover:border-neutral-300 transition-colors"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="font-medium text-neutral-900">{imp.filename}</h3>
                      <p className="text-sm text-neutral-500 mt-0.5">
                        {new Date(imp.created_at).toLocaleString()}
                      </p>
                    </div>
                    {getStatusBadge(imp.status)}
                  </div>

                  <div className="grid grid-cols-6 gap-3 text-sm mb-3">
                    <div>
                      <p className="text-neutral-600">Total</p>
                      <p className="font-semibold text-neutral-900">{imp.total_rows}</p>
                    </div>
                    <div>
                      <p className="text-neutral-600">New</p>
                      <p className="font-semibold text-emerald-600">{imp.imported_count}</p>
                    </div>
                    <div>
                      <p className="text-neutral-600">Updated</p>
                      <p className="font-semibold text-blue-600">{imp.updated_count}</p>
                    </div>
                    <div>
                      <p className="text-neutral-600">Duplicates</p>
                      <p className="font-semibold text-neutral-600">{imp.duplicates_count}</p>
                    </div>
                    <div>
                      <p className="text-neutral-600">Enriched</p>
                      <p className="font-semibold text-neutral-900">{imp.enriched_count}</p>
                    </div>
                    <div>
                      <p className="text-neutral-600">Signals</p>
                      <p className="font-semibold text-neutral-900">{imp.signals_count}</p>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    {imp.status === 'completed' && (
                      <button
                        onClick={() => handleReprocess(imp.id)}
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-neutral-100 text-neutral-700 rounded text-sm font-medium hover:bg-neutral-200"
                      >
                        <RefreshCw className="w-3.5 h-3.5" />
                        Reprocess
                      </button>
                    )}
                    <button
                      onClick={() => handleDelete(imp.id)}
                      className="flex items-center gap-1.5 px-3 py-1.5 bg-red-50 text-red-700 rounded text-sm font-medium hover:bg-red-100"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
