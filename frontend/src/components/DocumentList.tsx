import React, { useState } from 'react';
import { 
  FileText, 
  Download, 
  Trash2, 
  Eye, 
  Search, 
  Filter, 
  User,
  Tag,
  AlertCircle,
  RefreshCw
} from 'lucide-react';

interface Document {
  id: string;
  filename: string;
  size: number;
  type: string;
  uploaded_by: string;
  upload_date: string;
  case_id?: string;
  description?: string;
  document_type: string;
}

interface DocumentListProps {
  documents: Document[];
  onDownload: (documentId: string, filename: string) => void;
  onDelete?: (documentId: string) => void;
  onPreview?: (document: Document) => void;
  isLoading?: boolean;
  onRefresh?: () => void;
  showActions?: boolean;
  compact?: boolean;
}

const DOCUMENT_TYPE_LABELS: Record<string, string> = {
  general: 'General',
  evidence: 'Evidence',
  pleading: 'Pleading',
  motion: 'Motion',
  order: 'Court Order',
  judgment: 'Judgment',
  contract: 'Contract',
  correspondence: 'Correspondence',
};

const DOCUMENT_TYPE_COLORS: Record<string, string> = {
  general: 'bg-gray-100 text-gray-800',
  evidence: 'bg-blue-100 text-blue-800',
  pleading: 'bg-green-100 text-green-800',
  motion: 'bg-yellow-100 text-yellow-800',
  order: 'bg-red-100 text-red-800',
  judgment: 'bg-purple-100 text-purple-800',
  contract: 'bg-indigo-100 text-indigo-800',
  correspondence: 'bg-pink-100 text-pink-800',
};

const DocumentList: React.FC<DocumentListProps> = ({
  documents,
  onDownload,
  onDelete,
  onPreview,
  isLoading = false,
  onRefresh,
  showActions = true,
  compact = false,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [sortBy, setSortBy] = useState<'date' | 'name' | 'size' | 'type'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<string | null>(null);

  const filteredAndSortedDocuments = React.useMemo(() => {
    let filtered = documents;

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(doc =>
        doc.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doc.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doc.case_id?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by document type
    if (filterType !== 'all') {
      filtered = filtered.filter(doc => doc.document_type === filterType);
    }

    // Sort documents
    filtered.sort((a, b) => {
      let comparison = 0;

      switch (sortBy) {
        case 'date':
          comparison = new Date(a.upload_date).getTime() - new Date(b.upload_date).getTime();
          break;
        case 'name':
          comparison = a.filename.localeCompare(b.filename);
          break;
        case 'size':
          comparison = a.size - b.size;
          break;
        case 'type':
          comparison = a.document_type.localeCompare(b.document_type);
          break;
      }

      return sortOrder === 'desc' ? -comparison : comparison;
    });

    return filtered;
  }, [documents, searchTerm, filterType, sortBy, sortOrder]);

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString() + ' ' + 
           new Date(dateString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getFileIcon = (_filename: string, type: string) => {
    if (type.startsWith('image/')) {
      return <Eye className="h-4 w-4 text-blue-500" />;
    }
    return <FileText className="h-4 w-4 text-red-500" />;
  };

  const handleDelete = (documentId: string) => {
    setShowDeleteConfirm(documentId);
  };

  const confirmDelete = (documentId: string) => {
    if (onDelete) {
      onDelete(documentId);
    }
    setShowDeleteConfirm(null);
  };

  const uniqueDocumentTypes = [...new Set(documents.map(doc => doc.document_type))];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Loading documents...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Search and Filter Controls */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0 lg:space-x-4">
        <div className="flex-1 max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search documents..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="flex items-center space-x-4">
          {/* Document Type Filter */}
          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4 text-gray-500" />
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Types</option>
              {uniqueDocumentTypes.map(type => (
                <option key={type} value={type}>
                  {DOCUMENT_TYPE_LABELS[type] || type}
                </option>
              ))}
            </select>
          </div>

          {/* Sort Controls */}
          <div className="flex items-center space-x-2">
            <select
              value={`${sortBy}-${sortOrder}`}
              onChange={(e) => {
                const [field, order] = e.target.value.split('-');
                setSortBy(field as 'date' | 'name' | 'size' | 'type');
                setSortOrder(order as 'asc' | 'desc');
              }}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="date-desc">Newest First</option>
              <option value="date-asc">Oldest First</option>
              <option value="name-asc">Name A-Z</option>
              <option value="name-desc">Name Z-A</option>
              <option value="size-desc">Largest First</option>
              <option value="size-asc">Smallest First</option>
              <option value="type-asc">Type A-Z</option>
            </select>
          </div>

          {/* Refresh Button */}
          {onRefresh && (
            <button
              onClick={onRefresh}
              className="px-3 py-2 text-gray-600 hover:text-gray-900 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
              title="Refresh documents"
            >
              <RefreshCw className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>

      {/* Results Summary */}
      <div className="flex items-center justify-between text-sm text-gray-600">
        <span>
          Showing {filteredAndSortedDocuments.length} of {documents.length} documents
        </span>
        {searchTerm && (
          <button
            onClick={() => setSearchTerm('')}
            className="text-blue-600 hover:text-blue-800 underline"
          >
            Clear search
          </button>
        )}
      </div>

      {/* Documents Grid/List */}
      {filteredAndSortedDocuments.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No documents found</h3>
          <p className="text-gray-500">
            {searchTerm || filterType !== 'all'
              ? 'Try adjusting your search or filter criteria.'
              : 'Upload your first document to get started.'}
          </p>
        </div>
      ) : (
        <div className={compact 
          ? "space-y-2" 
          : "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        }>
          {filteredAndSortedDocuments.map((document) => (
            <div
              key={document.id}
              className={`bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow ${
                compact ? 'p-4' : 'p-6'
              }`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-start space-x-3 flex-1">
                  {getFileIcon(document.filename, document.type)}
                  <div className="flex-1 min-w-0">
                    <h3 className={`font-medium text-gray-900 truncate ${compact ? 'text-sm' : 'text-base'}`}>
                      {document.filename}
                    </h3>
                    <p className="text-xs text-gray-500 mt-1">
                      {formatFileSize(document.size)} • {formatDate(document.upload_date)}
                    </p>
                  </div>
                </div>

                {showActions && (
                  <div className="flex items-center space-x-1">
                    {onPreview && (
                      <button
                        onClick={() => onPreview(document)}
                        className="p-1 text-gray-400 hover:text-blue-600 rounded"
                        title="Preview document"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                    )}
                    <button
                      onClick={() => onDownload(document.id, document.filename)}
                      className="p-1 text-gray-400 hover:text-green-600 rounded"
                      title="Download document"
                    >
                      <Download className="h-4 w-4" />
                    </button>
                    {onDelete && (
                      <button
                        onClick={() => handleDelete(document.id)}
                        className="p-1 text-gray-400 hover:text-red-600 rounded"
                        title="Delete document"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                )}
              </div>

              {/* Document Details */}
              <div className="space-y-2">
                {document.case_id && (
                  <div className="flex items-center space-x-2">
                    <Tag className="h-3 w-3 text-gray-400" />
                    <span className="text-xs text-gray-600">Case: {document.case_id}</span>
                  </div>
                )}

                <div className="flex items-center justify-between">
                  <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${
                    DOCUMENT_TYPE_COLORS[document.document_type] || 'bg-gray-100 text-gray-800'
                  }`}>
                    {DOCUMENT_TYPE_LABELS[document.document_type] || document.document_type}
                  </span>
                  
                  <div className="flex items-center space-x-1 text-xs text-gray-500">
                    <User className="h-3 w-3" />
                    <span>{document.uploaded_by}</span>
                  </div>
                </div>

                {document.description && (
                  <p className="text-xs text-gray-600 line-clamp-2" title={document.description}>
                    {document.description}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-mx">
            <div className="flex items-center space-x-3 mb-4">
              <AlertCircle className="h-6 w-6 text-red-600" />
              <h3 className="text-lg font-medium text-gray-900">Delete Document</h3>
            </div>
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete this document? This action cannot be undone.
            </p>
            <div className="flex space-x-3 justify-end">
              <button
                onClick={() => setShowDeleteConfirm(null)}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => confirmDelete(showDeleteConfirm)}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentList;