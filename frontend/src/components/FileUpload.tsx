import React, { useState, useRef } from 'react';
import { Upload, X, FileText, Image, FileIcon, AlertCircle } from 'lucide-react';

interface FileUploadProps {
  onUpload: (files: FileList, metadata: UploadMetadata) => Promise<void>;
  isUploading?: boolean;
  acceptedTypes?: string[];
  maxSize?: number; // in MB
  caseId?: string;
}

interface UploadMetadata {
  caseId?: string;
  description: string;
  documentType: string;
}

const DOCUMENT_TYPES = [
  { value: 'general', label: 'General Document' },
  { value: 'evidence', label: 'Evidence' },
  { value: 'pleading', label: 'Pleading' },
  { value: 'motion', label: 'Motion' },
  { value: 'order', label: 'Court Order' },
  { value: 'judgment', label: 'Judgment' },
  { value: 'contract', label: 'Contract' },
  { value: 'correspondence', label: 'Correspondence' },
];

const FileUpload: React.FC<FileUploadProps> = ({
  onUpload,
  isUploading = false,
  acceptedTypes = ['.pdf', '.doc', '.docx', '.txt', '.jpg', '.jpeg', '.png', '.gif'],
  maxSize = 10,
  caseId = '',
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [metadata, setMetadata] = useState<UploadMetadata>({
    caseId,
    description: '',
    documentType: 'general',
  });
  const [error, setError] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): string | null => {
    if (file.size > maxSize * 1024 * 1024) {
      return `File size must be less than ${maxSize}MB`;
    }

    const extension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!acceptedTypes.includes(extension)) {
      return `File type not allowed. Accepted types: ${acceptedTypes.join(', ')}`;
    }

    return null;
  };

  const handleFileSelect = (files: FileList) => {
    const validFiles: File[] = [];
    let errorMessage = '';

    Array.from(files).forEach(file => {
      const validation = validateFile(file);
      if (validation) {
        errorMessage = validation;
      } else {
        validFiles.push(file);
      }
    });

    if (errorMessage) {
      setError(errorMessage);
      return;
    }

    setError('');
    setSelectedFiles(validFiles);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    handleFileSelect(e.dataTransfer.files);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFileSelect(e.target.files);
    }
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;

    try {
      const fileList = new DataTransfer();
      selectedFiles.forEach(file => fileList.items.add(file));
      await onUpload(fileList.files, metadata);
      
      // Reset form
      setSelectedFiles([]);
      setMetadata({ caseId, description: '', documentType: 'general' });
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles(files => files.filter((_, i) => i !== index));
  };

  const getFileIcon = (fileName: string) => {
    const extension = fileName.split('.').pop()?.toLowerCase();
    
    if (['jpg', 'jpeg', 'png', 'gif'].includes(extension || '')) {
      return <Image className="h-4 w-4 text-blue-500" />;
    } else if (['pdf', 'doc', 'docx', 'txt'].includes(extension || '')) {
      return <FileText className="h-4 w-4 text-red-500" />;
    }
    
    return <FileIcon className="h-4 w-4 text-gray-500" />;
  };

  return (
    <div className="space-y-6">
      {/* Drag & Drop Area */}
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragOver
            ? 'border-blue-500 bg-blue-50'
            : selectedFiles.length > 0
            ? 'border-green-500 bg-green-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <p className="text-lg font-medium text-gray-900 mb-2">
          Drop files here or click to browse
        </p>
        <p className="text-sm text-gray-500 mb-4">
          Accepted files: {acceptedTypes.join(', ')} (max {maxSize}MB each)
        </p>
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          disabled={isUploading}
        >
          Select Files
        </button>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={acceptedTypes.join(',')}
          onChange={handleInputChange}
          className="hidden"
        />
      </div>

      {/* Error Message */}
      {error && (
        <div className="flex items-center space-x-2 text-red-600 bg-red-50 p-3 rounded-md">
          <AlertCircle className="h-5 w-5" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      {/* Selected Files */}
      {selectedFiles.length > 0 && (
        <div className="space-y-4">
          <h3 className="font-medium text-gray-900">Selected Files</h3>
          <div className="space-y-2">
            {selectedFiles.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-md"
              >
                <div className="flex items-center space-x-3">
                  {getFileIcon(file.name)}
                  <div>
                    <p className="text-sm font-medium text-gray-900">{file.name}</p>
                    <p className="text-xs text-gray-500">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="text-red-500 hover:text-red-700"
                  disabled={isUploading}
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>

          {/* Upload Metadata */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Case ID (Optional)
              </label>
              <input
                type="text"
                value={metadata.caseId}
                onChange={(e) => setMetadata({ ...metadata, caseId: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter case ID"
                disabled={isUploading}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Document Type
              </label>
              <select
                value={metadata.documentType}
                onChange={(e) => setMetadata({ ...metadata, documentType: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isUploading}
              >
                {DOCUMENT_TYPES.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description (Optional)
            </label>
            <textarea
              value={metadata.description}
              onChange={(e) => setMetadata({ ...metadata, description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
              placeholder="Enter document description..."
              disabled={isUploading}
            />
          </div>

          {/* Upload Button */}
          <button
            onClick={handleUpload}
            disabled={isUploading || selectedFiles.length === 0}
            className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {isUploading ? (
              <span className="flex items-center justify-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Uploading...</span>
              </span>
            ) : (
              `Upload ${selectedFiles.length} file${selectedFiles.length !== 1 ? 's' : ''}`
            )}
          </button>
        </div>
      )}
    </div>
  );
};

export default FileUpload;