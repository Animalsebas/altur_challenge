"use client";

import React, { useState, useCallback } from "react";
import { Upload } from "lucide-react";
import ReactMarkdown from "react-markdown"; // Import react-markdown

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
              : "border-gray-300 bg-white hover:border-blue-400 hover:bg-gray-50"
          }
        `}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <Upload className="w-10 h-10 mb-3" />
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

export default function Home() {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [transcription, setTranscription] = useState<string | null>(null);
  const [summary, setSummary] = useState<string | null>(null);
  const [tags, setTags] = useState<string[] | null>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const handleFileSelected = (file: File) => {
    setUploadedFile(file);
    setTranscription(null);
    setSummary(null);
    setTags(null);
  };

  const handleSubmit = async () => {
    if (!uploadedFile) {
      alert("Please upload a file before submitting.");
      return;
    }

    setIsSubmitting(true);

    const formData = new FormData();
    formData.append("file", uploadedFile);

    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to transcribe the file.");
      }

      const data = await response.json();
      console.log("Data received from API:", data);
      setTranscription(data.transcription);
      setSummary(data.summary);
      setTags(data.tags_list);
    } catch (error) {
      console.error("Error during transcription:", error);
      alert("An error occurred while transcribing the file.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="flex flex-col items-center justify-center gap-6 py-8 md:py-10">
      <h1 className="text-3xl font-bold">Altur: Sales Call Analyzer</h1>
      <p className="text-lg text-center max-w-2xl">
        Upload a call
      </p>

      <DragAndDropFileUploader onFileSelected={handleFileSelected} />

      {uploadedFile && (
        <div className="mt-4 p-4 border border-green-400 bg-green-50 rounded-lg text-green-800">
          <p className="font-semibold">File ready for analysis:</p>
          <p className="text-sm">Name: {uploadedFile.name}</p>
          <p className="text-sm">Size: {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB</p>
        </div>
      )}

      <button
        onClick={handleSubmit}
        disabled={isSubmitting}
        className={`mt-4 px-6 py-2 rounded-lg text-white ${
          isSubmitting ? "bg-gray-400 cursor-not-allowed" : "bg-blue-500 hover:bg-blue-600"
        }`}
      >
        {isSubmitting ? "Submitting..." : "Submit"}
      </button>

      {transcription && (
        <div className="mt-4 p-4 border border-blue-400 bg-blue-50 rounded-lg text-blue-800">
          <p className="font-semibold">Transcription:</p>
          <p className="text-sm">{transcription}</p>
        </div>
      )}

      {summary && (
        <div className="mt-4 p-4 border border-blue-400 bg-blue-50 rounded-lg text-blue-800">
          <p className="font-semibold">Summary:</p>
          <ReactMarkdown >{summary}</ReactMarkdown>
        </div>
      )}

      {tags && (
        <div className="mt-4 p-4 border border-blue-400 bg-blue-50 rounded-lg text-blue-800 w-full max-w-lg">
          <p className="font-semibold">Tags:</p>
          <ul className="mt-2 flex flex-wrap gap-2">
            {tags.map((tag, index) => (
              <li
                key={index}
                className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
              >
                {tag}
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}