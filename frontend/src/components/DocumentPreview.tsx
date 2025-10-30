import React, { useEffect, useState } from 'react';
import { X, Download, ExternalLink } from 'lucide-react';

interface DocumentPreviewProps {
  document: {
    id: string;
    filename: string;
    type: string;
    size: number;
    upload_date: string;
    description?: string;
    case_id?: string;
  };
  onClose: () => void;
  onDownload: (documentId: string, filename: string) => void;
}

const DocumentPreview: React.FC<DocumentPreviewProps> = ({
  document,
  onClose,
  onDownload,
}) => {
  const [previewUrl, setPreviewUrl] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string>('');

  const isImage = document.type.startsWith('image/');
  const isPDF = document.type === 'application/pdf';
  const isText = document.type === 'text/plain';

  useEffect(() => {
    const fetchPreview = async () => {
      setIsLoading(true);
      setError('');
      
      const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
      
      try {
        const response = await fetch(
          `http://localhost:8000/api/documents/${document.id}/preview`,
          {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        );

        if (!response.ok) {
          throw new Error('Failed to load preview');
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        setPreviewUrl(url);
      } catch (err) {
        setError('Failed to load preview');
        console.error('Preview error:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPreview();

    // Cleanup function to revoke object URL
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [document.id]);

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex-1">
            <h2 className="text-xl font-semibold text-gray-900 truncate">
              {document.filename}
            </h2>
            <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600">
              <span>{formatFileSize(document.size)}</span>
              <span>•</span>
              <span>{new Date(document.upload_date).toLocaleDateString()}</span>
              {document.case_id && (
                <>
                  <span>•</span>
                  <span>Case: {document.case_id}</span>
                </>
              )}
            </div>
            {document.description && (
              <p className="mt-2 text-sm text-gray-600">{document.description}</p>
            )}
          </div>
          
          <div className="flex items-center space-x-2 ml-4">
            <button
              onClick={() => onDownload(document.id, document.filename)}
              className="p-2 text-gray-400 hover:text-blue-600 rounded-lg hover:bg-blue-50"
              title="Download document"
            >
              <Download className="h-5 w-5" />
            </button>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-red-600 rounded-lg hover:bg-red-50"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Preview Content */}
        <div className="flex-1 overflow-hidden">
          {isLoading && (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Loading preview...</p>
              </div>
            </div>
          )}

          {error && !isLoading && (
            <div className="h-full flex items-center justify-center p-6">
              <div className="text-center">
                <ExternalLink className="h-16 w-16 text-red-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Preview Error
                </h3>
                <p className="text-gray-600 mb-6">{error}</p>
                <button
                  onClick={() => onDownload(document.id, document.filename)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <Download className="h-4 w-4 inline mr-2" />
                  Download File
                </button>
              </div>
            </div>
          )}

          {!isLoading && !error && previewUrl && (
            <>
              {isImage && (
                <div className="h-full flex items-center justify-center p-6 bg-gray-50">
                  <img
                    src={previewUrl}
                    alt={document.filename}
                    className="max-w-full max-h-full object-contain rounded-lg shadow-sm"
                  />
                </div>
              )}

              {isPDF && (
                <div className="h-full">
                  <iframe
                    src={`${previewUrl}#toolbar=1&navpanes=1&scrollbar=1`}
                    className="w-full h-full border-0"
                    title={document.filename}
                  />
                </div>
              )}

              {isText && (
                <div className="h-full p-6 overflow-auto">
                  <div className="bg-gray-50 rounded-lg p-4 font-mono text-sm">
                    <iframe
                      src={previewUrl}
                      className="w-full h-96 border-0 bg-white rounded"
                      title={document.filename}
                    />
                  </div>
                </div>
              )}

              {!isImage && !isPDF && !isText && (
                <div className="h-full flex items-center justify-center p-6">
                  <div className="text-center">
                    <ExternalLink className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      Preview Not Available
                    </h3>
                    <p className="text-gray-600 mb-6">
                      This file type cannot be previewed in the browser. 
                      You can download the file to view it.
                    </p>
                    <button
                      onClick={() => onDownload(document.id, document.filename)}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      <Download className="h-4 w-4 inline mr-2" />
                      Download File
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default DocumentPreview;