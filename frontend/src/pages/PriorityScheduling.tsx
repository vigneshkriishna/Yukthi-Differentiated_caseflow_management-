import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Calendar,
  Clock,
  AlertTriangle,
  TrendingUp,
  CheckCircle,
  XCircle,
  Zap,
  Target,
  Filter,
  Play,
  RefreshCw
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

interface Case {
  id: number;
  case_number: string;
  title: string;
  case_type: string;
  priority: string;
  status: string;
  filing_date: string;
  estimated_duration_minutes: number;
}

interface SchedulingResult {
  scheduled_hearings: Array<{
    case_id: number;
    case_number: string;
    hearing_date: string;
    start_time: string;
    bench_id: number;
  }>;
  unplaced_cases: Array<{
    case_id: number;
    case_number: string;
    reason: string;
  }>;
  statistics: {
    total_scheduled: number;
    by_priority: Record<string, number>;
  };
}

const API_BASE = 'http://localhost:8000';

const PriorityScheduling: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const {} = useAuth();
  const [cases, setCases] = useState<Case[]>([]);
  const [selectedCases, setSelectedCases] = useState<number[]>([]);
  const [filterPriority, setFilterPriority] = useState<string>('all');
  const [strategy, setStrategy] = useState<string>('priority_first');
  const [daysAhead, setDaysAhead] = useState<number>(14);
  const [isLoading, setIsLoading] = useState(false);
  const [isScheduling, setIsScheduling] = useState(false);
  const [result, setResult] = useState<SchedulingResult | null>(null);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');

  // Check for URL parameters from Smart Scheduling
  useEffect(() => {
    const priority = searchParams.get('priority');
    const action = searchParams.get('action');
    
    if (priority && priority !== 'all') {
      setFilterPriority(priority);
    }
    
    if (action) {
      // Show a message about what action was suggested
      setSuccess(`Applying AI suggestion: ${action.replace(/_/g, ' ')}`);
      setTimeout(() => setSuccess(''), 5000);
    }
  }, [searchParams]);

  const getAuthToken = () => {
    return localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
  };

  useEffect(() => {
    loadPendingCases();
  }, []);

  const loadPendingCases = async () => {
    const token = getAuthToken();
    if (!token) {
      navigate('/login');
      return;
    }

    try {
      setIsLoading(true);
      const response = await fetch(`${API_BASE}/api/cases?status=filed&status=under_review`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setCases(data);
        setError('');
      } else if (response.status === 401) {
        navigate('/login');
      } else {
        setError('Failed to load pending cases');
      }
    } catch (err) {
      setError('Network error: Could not load cases');
      console.error('Error loading cases:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleScheduleSelected = async () => {
    if (selectedCases.length === 0) {
      setError('Please select at least one case to schedule');
      return;
    }

    const token = getAuthToken();
    if (!token) {
      navigate('/login');
      return;
    }

    try {
      setIsScheduling(true);
      setError('');
      setSuccess('');

      const response = await fetch(`${API_BASE}/schedule/smart-schedule`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          case_ids: selectedCases,
          strategy: strategy,
          days_ahead: daysAhead
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setResult(data.scheduling_result);
        setSuccess(`Successfully scheduled ${data.scheduling_result.scheduled_hearings.length} cases!`);
        setSelectedCases([]);
        
        // Reload cases to update status
        await loadPendingCases();
      } else if (response.status === 401) {
        navigate('/login');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to schedule cases');
      }
    } catch (err) {
      setError('Network error: Could not schedule cases');
      console.error('Error scheduling cases:', err);
    } finally {
      setIsScheduling(false);
    }
  };

  const toggleCaseSelection = (caseId: number) => {
    setSelectedCases(prev =>
      prev.includes(caseId)
        ? prev.filter(id => id !== caseId)
        : [...prev, caseId]
    );
  };

  const selectAllByPriority = (priority: string) => {
    const priorityCases = filteredCases
      .filter(c => c.priority.toLowerCase() === priority.toLowerCase())
      .map(c => c.id);
    setSelectedCases(prev => [...new Set([...prev, ...priorityCases])]);
  };

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      urgent: 'bg-red-100 text-red-800 border-red-300',
      high: 'bg-orange-100 text-orange-800 border-orange-300',
      medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      low: 'bg-gray-100 text-gray-800 border-gray-300'
    };
    return colors[priority.toLowerCase()] || 'bg-gray-100 text-gray-800';
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'urgent':
        return <AlertTriangle className="h-4 w-4" />;
      case 'high':
        return <Zap className="h-4 w-4" />;
      default:
        return <Target className="h-4 w-4" />;
    }
  };

  const filteredCases = cases.filter(c =>
    filterPriority === 'all' || c.priority.toLowerCase() === filterPriority
  );

  const priorityStats = {
    urgent: cases.filter(c => c.priority.toLowerCase() === 'urgent').length,
    high: cases.filter(c => c.priority.toLowerCase() === 'high').length,
    medium: cases.filter(c => c.priority.toLowerCase() === 'medium').length,
    low: cases.filter(c => c.priority.toLowerCase() === 'low').length,
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 flex items-center">
                <Calendar className="h-7 w-7 text-blue-600 mr-3" />
                Priority-Based Case Scheduling
              </h1>
              <p className="text-gray-600 mt-1">
                Intelligently schedule cases based on priority and availability
              </p>
            </div>
            <button
              onClick={loadPendingCases}
              className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              disabled={isLoading}
            >
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Status Messages */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <XCircle className="h-5 w-5 text-red-400" />
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

        {/* Priority Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-red-600">Urgent</p>
                <p className="text-2xl font-bold text-red-900">{priorityStats.urgent}</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-red-500" />
            </div>
            <button
              onClick={() => selectAllByPriority('urgent')}
              className="mt-2 text-xs text-red-700 hover:text-red-900 underline"
            >
              Select All
            </button>
          </div>

          <div className="bg-orange-50 border-2 border-orange-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-orange-600">High Priority</p>
                <p className="text-2xl font-bold text-orange-900">{priorityStats.high}</p>
              </div>
              <Zap className="h-8 w-8 text-orange-500" />
            </div>
            <button
              onClick={() => selectAllByPriority('high')}
              className="mt-2 text-xs text-orange-700 hover:text-orange-900 underline"
            >
              Select All
            </button>
          </div>

          <div className="bg-yellow-50 border-2 border-yellow-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-yellow-600">Medium Priority</p>
                <p className="text-2xl font-bold text-yellow-900">{priorityStats.medium}</p>
              </div>
              <Target className="h-8 w-8 text-yellow-500" />
            </div>
            <button
              onClick={() => selectAllByPriority('medium')}
              className="mt-2 text-xs text-yellow-700 hover:text-yellow-900 underline"
            >
              Select All
            </button>
          </div>

          <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Low Priority</p>
                <p className="text-2xl font-bold text-gray-900">{priorityStats.low}</p>
              </div>
              <TrendingUp className="h-8 w-8 text-gray-500" />
            </div>
            <button
              onClick={() => selectAllByPriority('low')}
              className="mt-2 text-xs text-gray-700 hover:text-gray-900 underline"
            >
              Select All
            </button>
          </div>
        </div>

        {/* Scheduling Controls */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Scheduling Configuration</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Filter className="inline h-4 w-4 mr-1" />
                Filter by Priority
              </label>
              <select
                value={filterPriority}
                onChange={(e) => setFilterPriority(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Priorities</option>
                <option value="urgent">Urgent</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Scheduling Strategy
              </label>
              <select
                value={strategy}
                onChange={(e) => setStrategy(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="priority_first">Priority First</option>
                <option value="fifo">First In First Out</option>
                <option value="balanced">Balanced</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Schedule Within (Days)
              </label>
              <input
                type="number"
                value={daysAhead}
                onChange={(e) => setDaysAhead(parseInt(e.target.value))}
                min={7}
                max={30}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div className="flex items-center justify-between pt-4 border-t border-gray-200">
            <div className="text-sm text-gray-600">
              {selectedCases.length} case(s) selected
            </div>
            <div className="flex space-x-3">
              <button
                onClick={() => setSelectedCases([])}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                disabled={selectedCases.length === 0}
              >
                Clear Selection
              </button>
              <button
                onClick={handleScheduleSelected}
                disabled={selectedCases.length === 0 || isScheduling}
                className="flex items-center space-x-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Play className="h-4 w-4" />
                <span>{isScheduling ? 'Scheduling...' : 'Schedule Selected Cases'}</span>
              </button>
            </div>
          </div>
        </div>

        {/* Cases List */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">
              Pending Cases ({filteredCases.length})
            </h2>
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="ml-2 text-gray-600">Loading cases...</span>
            </div>
          ) : filteredCases.length === 0 ? (
            <div className="text-center py-12">
              <Calendar className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No pending cases</h3>
              <p className="text-gray-500">All cases have been scheduled!</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left">
                      <input
                        type="checkbox"
                        checked={selectedCases.length === filteredCases.length && filteredCases.length > 0}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedCases(filteredCases.map(c => c.id));
                          } else {
                            setSelectedCases([]);
                          }
                        }}
                        className="h-4 w-4 text-blue-600 border-gray-300 rounded"
                      />
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Case Number
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Title
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Priority
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Filing Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Duration
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredCases.map((caseItem) => (
                    <tr
                      key={caseItem.id}
                      className={`hover:bg-gray-50 cursor-pointer ${
                        selectedCases.includes(caseItem.id) ? 'bg-blue-50' : ''
                      }`}
                      onClick={() => toggleCaseSelection(caseItem.id)}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <input
                          type="checkbox"
                          checked={selectedCases.includes(caseItem.id)}
                          onChange={() => toggleCaseSelection(caseItem.id)}
                          onClick={(e) => e.stopPropagation()}
                          className="h-4 w-4 text-blue-600 border-gray-300 rounded"
                        />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">
                        {caseItem.case_number}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">
                        {caseItem.title}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-medium border ${getPriorityColor(caseItem.priority)}`}>
                          {getPriorityIcon(caseItem.priority)}
                          <span className="ml-1">{caseItem.priority}</span>
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {caseItem.case_type}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(caseItem.filing_date).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <div className="flex items-center">
                          <Clock className="h-4 w-4 mr-1" />
                          {caseItem.estimated_duration_minutes} min
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Scheduling Result */}
        {result && (
          <div className="mt-6 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Scheduling Results</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-sm font-medium text-green-600 mb-2">
                  <CheckCircle className="inline h-4 w-4 mr-1" />
                  Successfully Scheduled ({result.scheduled_hearings.length})
                </h3>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {result.scheduled_hearings.map((hearing, idx) => (
                    <div key={idx} className="text-sm p-2 bg-green-50 border border-green-200 rounded">
                      <div className="font-medium text-green-900">{hearing.case_number}</div>
                      <div className="text-green-700">
                        {new Date(hearing.hearing_date).toLocaleDateString()} at {hearing.start_time}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {result.unplaced_cases.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-orange-600 mb-2">
                    <AlertTriangle className="inline h-4 w-4 mr-1" />
                    Could Not Schedule ({result.unplaced_cases.length})
                  </h3>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {result.unplaced_cases.map((unplaced, idx) => (
                      <div key={idx} className="text-sm p-2 bg-orange-50 border border-orange-200 rounded">
                        <div className="font-medium text-orange-900">{unplaced.case_number}</div>
                        <div className="text-orange-700">{unplaced.reason}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PriorityScheduling;
