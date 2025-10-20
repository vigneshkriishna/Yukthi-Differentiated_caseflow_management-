import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { 
  Upload, 
  FileText, 
  BarChart3, 
  Grid,
  List,
  Download,
  AlertCircle,
  CheckCircle,
  Clock,
  Shield
} from 'lucide-react';
import FileUpload from '../components/FileUpload';
import DocumentList from '../components/DocumentList';
import DocumentPreview from '../components/DocumentPreview';
import { useAuth, usePermissions } from '../contexts/AuthContext';

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

interface UploadMetadata {
  caseId?: string;
  description: string;
  documentType: string;
}

interface DocumentStats {
  total: number;
  byType: Record<string, number>;
  totalSize: number;
  recentUploads: number;
}

const API_BASE = 'http://localhost:8001';

const Documents: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { user } = useAuth();
  const permissions = usePermissions();

  // Debug: Confirm component is rendering
  React.useEffect(() => {
    console.log('🗂️ DOCUMENTS COMPONENT MOUNTED - This is the Documents page, NOT Dashboard!');
    document.title = 'Documents - DCM System';
  }, []);

  // Get URL parameters
  const urlCaseId = searchParams.get('caseId');
  const urlTab = searchParams.get('tab');

  // Check if user has document upload permission using the permission system
  const canUpload = permissions.canCreate('documents');
  const canDelete = permissions.canDelete('documents') || permissions.isAdmin || permissions.isClerk;

  console.log('🔍 Documents Page - Permission Check:', {
    user: user?.username,
    role: user?.role,
    canUpload,
    canDelete,
    isClerk: permissions.isClerk,
    isAdmin: permissions.isAdmin,
    rawPermissions: {
      canCreateDocuments: permissions.canCreate('documents'),
      hasPermission: permissions.hasPermission('documents.create')
    }
  });

  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'upload' | 'list' | 'analytics'>(
    (urlTab === 'upload' && canUpload) ? 'upload' : 'list'
  );
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [previewDocument, setPreviewDocument] = useState<Document | null>(null);
  const [stats, setStats] = useState<DocumentStats>({
    total: 0,
    byType: {},
    totalSize: 0,
    recentUploads: 0
  });

  const getAuthToken = () => {
    return localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
  };

  const loadDocuments = async () => {
    const token = getAuthToken();
    if (!token) {
      console.error('No auth token found, redirecting to login');
      localStorage.clear();
      sessionStorage.clear();
      navigate('/login', { replace: true });
      return;
    }

    try {
      setIsLoading(true);
      const response = await fetch(`${API_BASE}/api/documents`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setDocuments(data);
        calculateStats(data);
        setError('');
      } else if (response.status === 401) {
        console.error('401 Unauthorized - Token invalid or expired, redirecting to login');
        localStorage.clear();
        sessionStorage.clear();
        navigate('/login', { replace: true });
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to load documents');
      }
    } catch (err) {
      setError('Network error: Could not load documents');
      console.error('Error loading documents:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const calculateStats = (docs: Document[]) => {
    const now = new Date();
    const twentyFourHoursAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);

    const byType: Record<string, number> = {};
    let totalSize = 0;
    let recentUploads = 0;

    docs.forEach(doc => {
      byType[doc.document_type] = (byType[doc.document_type] || 0) + 1;
      totalSize += doc.size;
      
      if (new Date(doc.upload_date) > twentyFourHoursAgo) {
        recentUploads++;
      }
    });

    setStats({
      total: docs.length,
      byType,
      totalSize,
      recentUploads
    });
  };

  const handleUpload = async (files: FileList, metadata: UploadMetadata) => {
    const token = getAuthToken();
    if (!token) {
      navigate('/login');
      return;
    }

    setIsUploading(true);
    setError('');
    setSuccess('');

    try {
      const uploadPromises = Array.from(files).map(async (file) => {
        const formData = new FormData();
        formData.append('file', file);
        if (metadata.caseId) formData.append('case_id', metadata.caseId);
        if (metadata.description) formData.append('description', metadata.description);
        formData.append('document_type', metadata.documentType);

        const response = await fetch(`${API_BASE}/api/documents/upload`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
          body: formData,
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || `Failed to upload ${file.name}`);
        }

        return response.json();
      });

      await Promise.all(uploadPromises);
      const caseText = urlCaseId ? ` for Case ${urlCaseId}` : '';
      setSuccess(`Successfully uploaded ${files.length} file${files.length !== 1 ? 's' : ''}${caseText}`);
      await loadDocuments(); // Refresh the document list
      
      // Auto-switch to list view after successful upload
      if (activeTab === 'upload') {
        setActiveTab('list');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDownload = async (documentId: string, filename: string) => {
    const token = getAuthToken();
    if (!token) return;

    try {
      const response = await fetch(`${API_BASE}/api/documents/${documentId}/download`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Download failed');
      }
    } catch (err) {
      setError('Download failed');
    }
  };

  const handleDelete = async (documentId: string) => {
    const token = getAuthToken();
    if (!token) return;

    try {
      const response = await fetch(`${API_BASE}/api/documents/${documentId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setSuccess('Document deleted successfully');
        await loadDocuments(); // Refresh the document list
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Delete failed');
      }
    } catch (err) {
      setError('Delete failed');
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  // Auto-clear messages after 5 seconds
  useEffect(() => {
    if (success || error) {
      const timer = setTimeout(() => {
        setSuccess('');
        setError('');
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [success, error]);

  const renderAnalytics = () => {
    const documentTypes = Object.entries(stats.byType).map(([type, count]) => ({
      type: type.charAt(0).toUpperCase() + type.slice(1),
      count,
      percentage: Math.round((count / stats.total) * 100)
    }));

    return (
      <div className="space-y-6">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center">
              <FileText className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Documents</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center">
              <Download className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Size</p>
                <p className="text-2xl font-bold text-gray-900">{formatFileSize(stats.totalSize)}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center">
              <Clock className="h-8 w-8 text-orange-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Recent (24h)</p>
                <p className="text-2xl font-bold text-gray-900">{stats.recentUploads}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center">
              <BarChart3 className="h-8 w-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Document Types</p>
                <p className="text-2xl font-bold text-gray-900">{Object.keys(stats.byType).length}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Document Types Breakdown */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Documents by Type</h3>
          <div className="space-y-4">
            {documentTypes.map(({ type, count, percentage }) => (
              <div key={type} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0 w-4 h-4 bg-blue-500 rounded"></div>
                  <span className="text-sm font-medium text-gray-900">{type}</span>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full" 
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                  <span className="text-sm text-gray-600 w-12 text-right">{count}</span>
                  <span className="text-sm text-gray-500 w-8 text-right">{percentage}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-3">
            {documents
              .slice(0, 5)
              .map(doc => (
                <div key={doc.id} className="flex items-center justify-between py-2">
                  <div className="flex items-center space-x-3">
                    <FileText className="h-4 w-4 text-gray-400" />
                    <span className="text-sm text-gray-900">{doc.filename}</span>
                  </div>
                  <span className="text-sm text-gray-500">
                    {new Date(doc.upload_date).toLocaleDateString()}
                  </span>
                </div>
              ))}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 flex items-center">
                <FileText className="h-7 w-7 text-blue-600 mr-3" />
                Document Management System
                {urlCaseId && <span className="text-lg font-normal text-blue-600"> - Case {urlCaseId}</span>}
              </h1>
              <p className="text-gray-600">
                {urlCaseId 
                  ? `Manage documents for Case ${urlCaseId}` 
                  : 'Upload, organize, and manage case documents securely'
                }
              </p>
              
              {/* Permission Info */}
              <div className="mt-2 flex items-center space-x-4 text-sm">
                <div className="flex items-center space-x-1">
                  <Shield className="h-4 w-4 text-blue-500" />
                  <span className="text-gray-600">Your Role: </span>
                  <span className="font-medium text-gray-900">{user?.role}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <span className="text-gray-600">Permissions: </span>
                  <span className="text-green-600">
                    View, Download{canUpload && ', Upload'}{canDelete && ', Delete'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="flex space-x-8 -mb-px">
            {[
              { id: 'list', label: 'Documents', icon: FileText, show: true },
              { id: 'upload', label: 'Upload', icon: Upload, show: canUpload },
              { id: 'analytics', label: 'Analytics', icon: BarChart3, show: true },
            ]
            .filter(tab => tab.show)
            .map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id as 'upload' | 'list' | 'analytics')}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Status Messages */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <AlertCircle className="h-5 w-5 text-red-400" />
              <div className="ml-3">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            </div>
          </div>
        )}

        {success && (
          <div className="mb-6 bg-green-50 border border-green-200 rounded-md p-4">
            <div className="flex">
              <CheckCircle className="h-5 w-5 text-green-400" />
              <div className="ml-3">
                <p className="text-sm text-green-800">{success}</p>
              </div>
            </div>
          </div>
        )}

        {/* Case-Specific Banner */}
        {urlCaseId && (
          <div className="mb-6 bg-blue-50 border border-blue-200 rounded-md p-4">
            <div className="flex items-center space-x-2">
              <FileText className="h-5 w-5 text-blue-600" />
              <div>
                <h3 className="text-sm font-medium text-blue-900">
                  Viewing documents for Case {urlCaseId}
                </h3>
                <p className="text-sm text-blue-700">
                  Only documents associated with this case are shown. 
                  <button 
                    onClick={() => navigate('/documents')}
                    className="ml-2 underline hover:no-underline"
                  >
                    View all documents
                  </button>
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Tab Content */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          {activeTab === 'upload' && (
            <div>
              <>
                <div className="mb-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-2">Upload Documents</h2>
                  <p className="text-gray-600">
                    Upload documents related to your cases. Supported formats: PDF, DOC, DOCX, TXT, JPG, PNG, GIF
                  </p>
                  <div className="mt-2 flex items-center space-x-2 text-sm text-blue-600">
                    <Shield className="h-4 w-4" />
                    <span>You have {user?.role || 'User'} access - document upload enabled</span>
                  </div>
                </div>
                <FileUpload
                  onUpload={handleUpload}
                  isUploading={isUploading}
                  maxSize={10}
                  caseId={urlCaseId || ''}
                />
              </>
            </div>
          )}

          {activeTab === 'list' && (
            <div>
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">All Documents</h2>
                  <p className="text-gray-600">Manage and organize your uploaded documents</p>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setViewMode('grid')}
                    className={`p-2 rounded-md ${
                      viewMode === 'grid'
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-400 hover:text-gray-600'
                    }`}
                  >
                    <Grid className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => setViewMode('list')}
                    className={`p-2 rounded-md ${
                      viewMode === 'list'
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-400 hover:text-gray-600'
                    }`}
                  >
                    <List className="h-4 w-4" />
                  </button>
                </div>
              </div>
              
              <DocumentList
                documents={urlCaseId ? documents.filter(doc => doc.case_id === urlCaseId) : documents}
                onDownload={handleDownload}
                onDelete={canDelete ? handleDelete : undefined}
                onPreview={setPreviewDocument}
                isLoading={isLoading}
                onRefresh={loadDocuments}
                compact={viewMode === 'list'}
              />
            </div>
          )}

          {activeTab === 'analytics' && (
            <div>
              <div className="mb-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-2">Document Analytics</h2>
                <p className="text-gray-600">
                  Insights and statistics about your document collection
                </p>
              </div>
              {renderAnalytics()}
            </div>
          )}
        </div>
      </div>

      {/* Document Preview Modal */}
      {previewDocument && (
        <DocumentPreview
          document={previewDocument}
          onClose={() => setPreviewDocument(null)}
          onDownload={handleDownload}
        />
      )}
    </div>
  );
};

export default Documents;