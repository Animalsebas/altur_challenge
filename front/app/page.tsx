"use client";

import React, { useState, useCallback, useEffect, useRef } from "react";
import { Upload } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { CallAnalysisLoader } from '@/components/loader';
import {Button} from "@heroui/button";
import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  useDisclosure,
} from "@heroui/modal";

type Toast = {
  id: number;
  message: string;
  type?: "success" | "error" | "info";
};

type DragAndDropFileUploaderProps = {
  onFileSelected: (file: File) => void;
};

const DragAndDropFileUploader: React.FC<DragAndDropFileUploaderProps> = ({ onFileSelected }) => {
  const [isDragging, setIsDragging] = useState<boolean>(false);

  const handleFileChange = useCallback(
    (files: FileList | null) => {
      if (files && files.length > 0) {
        const file = files[0];
        if (file.type === "audio/mp3" || file.type === "audio/wav" || file.type === "audio/mpeg") {
          onFileSelected(file);
        } else {
          alert("Unsupported file format. Please upload an mp3 or wav file.");
        }
      }
    },
    [onFileSelected]
  );

  const handleDrop = useCallback(
    (event: React.DragEvent<HTMLLabelElement>) => {
      event.preventDefault();
      setIsDragging(false);
      handleFileChange(event.dataTransfer.files);
    },
    [handleFileChange]
  );

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    handleFileChange(event.target.files);
  };

  const handleDragOver = (event: React.DragEvent<HTMLLabelElement>) => {
    event.preventDefault();
    if (!isDragging) setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  return (
    <div className="w-full max-w-lg mx-auto p-4">
      <label
        htmlFor="file-upload"
        className={`
          flex flex-col items-center justify-center 
          border-2 border-dashed rounded-lg p-10 cursor-pointer transition-colors duration-200
          ${
            isDragging
              ? "border-blue-500 bg-blue-50 text-blue-700"
              : "border-gray-300 hover:border-blue-400"
          }
        `}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <Upload className="w-10 h-10 mb-3 text-blue-500" stroke="currentColor" />
        <p className="text-lg font-semibold">
          {isDragging ? "Drop your file here" : "Drag & drop file or click to upload"}
        </p>
        <p className="text-sm text-gray-500 mt-1">Supported formats: **mp3 and wav**</p>

        <input
          id="file-upload"
          type="file"
          className="hidden"
          accept=".mp3, .wav"
          onChange={handleInputChange}
        />
      </label>
    </div>
  );
};

export default function App() {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [historyRows, setHistoryRows] = useState<
    { id: number; file_name: string; uploaded_at: string; tags: string[] }[] | null
  >(null);
  const [allAvailableTags, setAllAvailableTags] = useState<string[]>([]);
  const [activeFilterTags, setActiveFilterTags] = useState<string[]>([]);
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");
  const [isFilterDropdownOpen, setIsFilterDropdownOpen] = useState(false);
  const filterRef = useRef<HTMLDivElement | null>(null);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [selectedDetails, setSelectedDetails] = useState<any | null>(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [analysisMode, setAnalysisMode] = useState<"local" | "remote">("remote");
  const {isOpen, onOpen, onOpenChange} = useDisclosure();


  const showToast = (message: string, type: Toast["type"] = "info", duration = 4000) => {
    const id = Date.now() + Math.floor(Math.random() * 1000);
    setToasts((s) => [...s, { id, message, type }]);
    setTimeout(() => setToasts((s) => s.filter((t) => t.id !== id)), duration);
  };

  const handleFileSelected = (file: File) => {
    setUploadedFile(file);
  };

  const handleSubmit = async () => {
    if (!uploadedFile) {
      showToast("Please upload a file before submitting.", "error");
      return;
    }

    setIsAnalyzing(true);

    const formData = new FormData();
    formData.append("file", uploadedFile);
    formData.append("analysis_mode", analysisMode);

    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        showToast("Failed to analyze the file.", "error");
        throw new Error("Failed to analyze the file.");
      }

      const data = await response.json();
      showToast("File transcribed and analyzed successfully!", "success");
      setUploadedFile(null);
      fetchHistory();
      handleRowClick(data.id);
    } catch (error) {
      console.error("Error during transcription:", error);
      showToast("An error occurred while transcribing the file.", "error");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const fetchHistory = async () => {
    setHistoryLoading(true);
    try {
      const res = await fetch("/api/history");
      if (!res.ok) throw new Error("Failed to load history");
      const data = await res.json();
      setHistoryRows(data);
      setAllAvailableTags(extractUniqueTags(data));
    } catch (e) {
      console.error("Error fetching history:", e);
      setHistoryRows([]);
      showToast("Failed to load history.", "error");
    } finally {
      setHistoryLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const extractUniqueTags = useCallback((rows: typeof historyRows) => {
    if (!rows) return [];
    const tags = new Set<string>();
    rows.forEach(row => {
      if (Array.isArray(row.tags)) {
        row.tags.forEach(tag => tags.add(tag));
      }
    });
    return Array.from(tags).sort();
  }, []);

  const toggleFilterTag = (tag: string) => {
    setActiveFilterTags(prev => 
      prev.includes(tag) 
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    );
  };

  const resetFilters = () => {
    setActiveFilterTags([]);
    setSortDirection("desc");
  };

  const filteredAndSortedRows = React.useMemo(() => {
    if (!historyRows) return [];

    let rows = historyRows;
    if (activeFilterTags.length > 0) {
      rows = historyRows.filter(row => 
        row.tags.some(tag => activeFilterTags.includes(tag))
      );
    }

    return rows.slice().sort((a, b) => {
      const timestampA = new Date(a.uploaded_at).getTime();
      const timestampB = new Date(b.uploaded_at).getTime();

      if (sortDirection === "asc") {
        return timestampA - timestampB;
      } else {
        return timestampB - timestampA;
      }
    });
  }, [historyRows, activeFilterTags, sortDirection]);

  useEffect(() => {
    function handleDocClick(e: MouseEvent) {
      if (!isFilterDropdownOpen) return;
      const target = e.target as Node | null;
      if (filterRef.current && target && !filterRef.current.contains(target)) {
        setIsFilterDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleDocClick);
    return () => document.removeEventListener("mousedown", handleDocClick);
  }, [isFilterDropdownOpen]);

  const handleRowClick = async (id: number) => {
    setDetailsLoading(true);
    try {
      const res = await fetch(`/api/history/${id}`);
      if (!res.ok) {
        throw new Error("Failed to fetch details");
      }
      const data = await res.json();
      setSelectedDetails(data);
      onOpen();
    } catch (e) {
      console.error("Error fetching details:", e);
      showToast("Failed to load details.", "error");
    } finally {
      setDetailsLoading(false);
    }
  };

  const downloadJSON = (data: any, filename: string) => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  const handleRetrieveAll = async () => {
    try {
      const res = await fetch("/api/retrieve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tags: activeFilterTags,
          order: sortDirection
        })
      });

      if (!res.ok) throw new Error("Failed retrieving calls");

      const data = await res.json();
      downloadJSON(data, "retrieved_calls.json");
    } catch (e) {
      console.error(e);
      showToast("Failed to retrieve calls.", "error");
    }
  };

  const handleRetrieveSingle = async () => {
    if (!selectedDetails) return;

    try {
      const res = await fetch(`/api/retrieve/${selectedDetails.id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });

      if (!res.ok) throw new Error("Failed to retrieve call");

      const data = await res.json();
      downloadJSON(data, "retrieved_call.json");
    } catch (e) {
      console.error(e);
      showToast("Failed to retrieve call.", "error");
    }
  };


  if (isAnalyzing) {
    return <CallAnalysisLoader />;
  }

  return (
    <section className="flex flex-col items-center justify-center gap-6 py-8 md:py-10">
      <h1 className="text-4xl font-bold">Altur: Sales Call Analyzer</h1>
      <p className="text-2xl text-center font-bold">
        Upload a call
      </p>

      <DragAndDropFileUploader onFileSelected={handleFileSelected} />

      {uploadedFile && (
        <>
          <div className="mt-4 p-4 border border-green-400 bg-green-50 rounded-lg text-green-800">
            <p className="font-semibold text-center">File {uploadedFile.name} is ready for analysis</p>
            <p className="text-center text-xl mt-2">Select a processing option</p>

            <div className="mt-3 flex items-center gap-3">

              <label
                className={`flex items-center gap-2 px-3 py-1 rounded-md cursor-pointer transition ${
                  analysisMode === "remote" ? "bg-blue-600 text-white" : "bg-white text-gray-700 border border-gray-200"
                }`}
              >
                <input
                  type="radio"
                  name="analysisMode"
                  value="remote"
                  checked={analysisMode === "remote"}
                  onChange={() => setAnalysisMode("remote")}
                  className="hidden"
                />
                <span className="text-lg font-medium">OpenAI (remote)</span>
              </label>

              <label
                className={`flex items-center gap-2 px-3 py-1 rounded-md cursor-pointer transition ${
                  analysisMode === "local" ? "bg-blue-600 text-white" : "bg-white text-gray-700 border border-gray-200"
                }`}
              >
                <input
                  type="radio"
                  name="analysisMode"
                  value="local"
                  checked={analysisMode === "local"}
                  onChange={() => setAnalysisMode("local")}
                  className="hidden"
                />
                <span className="text-lg font-medium">Local (server)</span>
              </label>

            </div>
          </div>

          <Button
            onPress={handleSubmit}
            disabled={isAnalyzing}
            className={`mt-4 px-6 py-2 rounded-lg text-white ${
              isAnalyzing ? "bg-gray-400 cursor-not-allowed" : "bg-blue-500 hover:bg-blue-600"
            }`}
          >
            {isAnalyzing ? "Analyzing..." : "Start Analysis"}
          </Button>
      </>
      )}
      
      <div className="w-full max-w-4xl mt-8">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-3 gap-3">
          <h2 className="text-2xl font-semibold">History</h2>

          <div className="flex items-center gap-4">
              <div className="relative" ref={filterRef}>
                  <Button
                      onPress={() => setIsFilterDropdownOpen(prev => !prev)}
                      className="px-3 py-1 rounded-md text-sm whitespace-nowrap border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300"
                  >
                      Filter Tags ({activeFilterTags.length})
                  </Button>
                  
                  {isFilterDropdownOpen && (
                      <div className="absolute z-100 top-full mt-2 right-0 w-64 p-4 border border-gray-200 dark:border-gray-700 rounded-lg shadow-xl bg-white dark:bg-gray-900 max-h-60 overflow-y-auto">
                          <p className="text-sm font-semibold mb-2 text-gray-900 dark:text-white">Select Tags</p>
                          
                          {allAvailableTags.length > 0 ? (
                              <div className="flex flex-wrap gap-2">
                                  {allAvailableTags.map(tag => (
                                      <span
                                          key={tag}
                                          onClick={() => toggleFilterTag(tag)}
                                          className={`
                                              text-xs px-3 py-1 rounded-full cursor-pointer transition-colors duration-150
                                              ${
                                                  activeFilterTags.includes(tag) 
                                                  ? "bg-blue-600 text-white dark:bg-blue-400 dark:text-gray-900 font-bold"
                                                  : "bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600"
                                              }
                                          `}
                                      >
                                          {tag}
                                      </span>
                                  ))}
                              </div>
                          ) : (
                              <p className="text-xs text-gray-500">No tags available.</p>
                          )}
                      </div>
                  )}
              </div>
              
              {(activeFilterTags.length > 0 || sortDirection !== "desc") && (
                  <Button
                      onPress={resetFilters}
                      className="px-3 py-1 rounded-md text-sm bg-red-500 hover:bg-red-600 text-white whitespace-nowrap"
                      aria-label="Reset all filters"
                  >
                      Reset Filters
                  </Button>
              )}

              <Button
                  onPress={() => setSortDirection(prev => (prev === "asc" ? "desc" : "asc"))}
                  className="px-3 py-1 rounded-md text-sm whitespace-nowrap"
                  disabled={historyLoading}
              >
                  Uploaded At: {sortDirection === "desc" ? "Newest ↑" : "Oldest ↓"}
              </Button>

              <Button
                  onPress={fetchHistory}
                  className="px-3 py-1 rounded-md text-sm"
                  disabled={historyLoading}
              >
                  {historyLoading ? "Refreshing..." : "Refresh"}
              </Button>

              <Button
                onPress={handleRetrieveAll}
                className="px-3 py-1 rounded-md text-sm bg-green-600 hover:bg-green-700 text-white"
              >
                Download
              </Button>

          </div>
        </div>

        <div className="rounded shadow overflow-hidden">
          <div className="max-h-[56vh] overflow-y-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead>
                <tr>
                  <th className="sticky top-0 z-10 px-4 py-2 text-left text-md font-medium 
                                text-black dark:text-gray-200 font-bold
                                bg-gray-50 dark:bg-gray-800">
                    ID
                  </th>

                  <th className="sticky top-0 z-10 px-4 py-2 text-left text-md font-medium 
                                text-black dark:text-gray-200 font-bold
                                bg-gray-50 dark:bg-gray-800">
                    Filename
                  </th>

                  <th 
                    className="sticky top-0 z-10 px-4 py-2 text-left text-md font-medium 
                              text-black dark:text-gray-200 font-bold cursor-pointer
                              bg-gray-50 dark:bg-gray-800"
                    onClick={() => setSortDirection(prev => (prev === "asc" ? "desc" : "asc"))}
                  >
                    Uploaded At {sortDirection === "desc" ? " ↓" : " ↑"}
                  </th>

                  <th className="sticky top-0 z-10 px-4 py-2 text-left text-md font-medium 
                                text-black dark:text-gray-200 font-bold
                                bg-gray-50 dark:bg-gray-800">
                    Tags
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-100 dark:divide-gray-800">
                {filteredAndSortedRows.length > 0 ? (
                  filteredAndSortedRows.map((r) => (
                    <tr
                      key={r.id}
                      onClick={() => handleRowClick(r.id)}
                      className="hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
                    >
                      <td className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{r.id}</td>
                      <td className="px-4 py-3 text-sm text-gray-900 dark:text-white">{r.file_name}</td>
                      <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">
                        {new Date(r.uploaded_at).toLocaleString()}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex flex-wrap gap-2">
                          {Array.isArray(r.tags) && r.tags.length > 0 ? (
                            r.tags.map((t: string, i: number) => (
                              <span
                                key={i}
                                className="text-xs bg-blue-50 text-blue-700 dark:bg-blue-900 dark:text-blue-300 px-2 py-1 rounded-full"
                              >
                                {t}
                              </span>
                            ))
                          ) : (
                            <span className="text-xs text-gray-400 dark:text-gray-500">—</span>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td
                      colSpan={4}
                      className="px-4 py-6 text-center text-sm text-black dark:text-white font-bold"
                    >
                      {historyLoading
                        ? "Loading..."
                        : activeFilterTags.length > 0
                        ? "No results match your selected filters."
                        : "No history found."}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <Modal isOpen={isOpen} onOpenChange={onOpenChange} size="4xl">
        <ModalContent>
          {(onClose) => (
            <>
            <ModalHeader className="flex flex-col gap-1">Analysis Details</ModalHeader>
            <ModalBody>
            <div className="p-6 max-h-[70vh] overflow-y-auto space-y-4">
              {detailsLoading ? (
                <p>Loading details…</p>
              ) : selectedDetails ? (
                <>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm font-bold">ID</p>
                      <p className="font-medium">{selectedDetails.id}</p>
                    </div>
                    <div>
                      <p className="text-sm font-bold">Filename</p>
                      <p className="font-medium">{selectedDetails.file_name}</p>
                    </div>
                    <div>
                      <p className="text-sm font-bold">Uploaded At</p>
                      <p className="font-medium">
                        {new Date(selectedDetails.uploaded_at).toLocaleString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-bold">Language</p>
                      <p className="font-medium">{selectedDetails.language ?? "—"}</p>
                      <p className="text-xs text-gray-500 mt-1 italic">
                        Note: language is detected only when processed locally.
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-bold">Processed</p>
                      <p className="font-medium">{selectedDetails.processed_where}</p>
                    </div>
                  </div>

                  <div>
                    <p className="text-sm font-bold">Tags</p>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {Array.isArray(selectedDetails.tags) && selectedDetails.tags.length > 0 ? (
                        selectedDetails.tags.map((t: string, i: number) => (
                          <span key={i} className="text-sm bg-blue-50 text-blue-700 px-2 py-1 rounded-full">
                            {t}
                          </span>
                        ))
                      ) : (
                        <span className="text-sm text-gray-400">—</span>
                      )}
                    </div>
                  </div>

                  <div>
                    <p className="text-sm font-bold">Summary</p>
                    <div className="mt-2 prose max-w-none">
                      <ReactMarkdown>{selectedDetails.summary ?? ""}</ReactMarkdown>
                    </div>
                  </div>

                  <div>
                    <p className="text-sm font-bold">Full Transcript</p>
                      <pre 
                        className="whitespace-pre-wrap text-sm border border-gray-300 dark:border-gray-700 p-3 rounded mt-2 max-h-60 overflow-y-auto">                      
                      {selectedDetails.full_transcript ?? ""}
                    </pre>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm text-gray-700 dark:text-gray-300">
                    <div>
                      <p className="text-sm font-bold">Transcribe time (s)</p>
                      <p>{selectedDetails.transcribe_time ?? "—"}</p>
                    </div>
                    <div>
                      <p className="text-sm font-bold">Analysis time (s)</p>
                      <p>{selectedDetails.analysis_time ?? "—"}</p>
                    </div>
                  </div>
                </>
              ) : (
                <p className="text-lg font-bold">No details available.</p>
              )}
            </div>
            </ModalBody>
            <ModalFooter>
              <Button
                className="bg-green-600 text-white hover:bg-green-700"
                onPress={handleRetrieveSingle}
              >
                Download
              </Button>

              <Button color="danger" variant="light" onPress={onClose}>
                Close
              </Button>
            </ModalFooter>
            </>
          )}
        </ModalContent>
      </Modal>
          
    </section>
  );
}