import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { hearingsAPI } from '@/services/api';
import type { Hearing, HearingFilters } from '@/types';

const Hearings: React.FC = () => {
  const { user } = useAuth();
  const [hearings, setHearings] = useState<Hearing[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<HearingFilters>({});
  const [searchTerm, setSearchTerm] = useState('');

  // Mock data for demonstration
  const mockHearings: Hearing[] = [
    {
      id: 1,
      case_id: 1,
      bench_id: 1,
      judge_id: 1,
      scheduled_date: '2024-08-31',
      scheduled_time: '10:00',
      duration_minutes: 120,
      status: 'scheduled',
      notes: 'Criminal case hearing',
      created_at: '2024-08-30T10:00:00Z',
      updated_at: '2024-08-30T10:00:00Z',
    },
    {
      id: 2,
      case_id: 2,
      bench_id: 2,
      judge_id: 2,
      scheduled_date: '2024-08-31',
      scheduled_time: '14:00',
      duration_minutes: 90,
      status: 'scheduled',
      notes: 'Civil case hearing',
      created_at: '2024-08-30T11:00:00Z',
      updated_at: '2024-08-30T11:00:00Z',
    },
    {
      id: 3,
      case_id: 3,
      bench_id: 1,
      judge_id: 1,
      scheduled_date: '2024-09-01',
      scheduled_time: '09:30',
      duration_minutes: 60,
      status: 'completed',
      notes: 'Family case hearing - completed',
      created_at: '2024-08-29T09:00:00Z',
      updated_at: '2024-08-30T09:30:00Z',
    },
  ];

  useEffect(() => {
    loadHearings();
  }, [filters]);

  const loadHearings = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // For now, use mock data
      // In production, this would be: const response = await hearingsAPI.getAll();
      setTimeout(() => {
        setHearings(mockHearings);
        setLoading(false);
      }, 500);
    } catch (err) {
      setError('Failed to load hearings');
      setLoading(false);
      console.error('Error loading hearings:', err);
    }
  };

  const handleFilterChange = (key: keyof HearingFilters, value: string) => {
    setFilters(prev => ({
      ...prev,
      [key]: value || undefined,
    }));
  };

  const clearFilters = () => {
    setFilters({});
    setSearchTerm('');
  };

  const formatTime = (time: string | undefined) => {
    if (!time) return 'Not set';
    return new Date(`2000-01-01T${time}`).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'scheduled':
        return 'bg-blue-100 text-blue-800';
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'postponed':
        return 'bg-orange-100 text-orange-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredHearings = hearings.filter(hearing => {
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      const matchesSearch = 
        hearing.id.toString().includes(searchLower) ||
        hearing.case_id.toString().includes(searchLower) ||
        hearing.status.toLowerCase().includes(searchLower) ||
        hearing.notes?.toLowerCase().includes(searchLower);
      
      if (!matchesSearch) return false;
    }

    if (filters.status && hearing.status !== filters.status) return false;
    if (filters.bench_id && hearing.bench_id !== Number(filters.bench_id)) return false;
    if (filters.judge_id && hearing.judge_id !== Number(filters.judge_id)) return false;
    if (filters.date_from && hearing.scheduled_date < filters.date_from) return false;
    if (filters.date_to && hearing.scheduled_date > filters.date_to) return false;

    return true;
  });

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">Loading hearings...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Hearings Schedule</h1>
        <div className="flex gap-2">
          {(user?.role === 'admin' || user?.role === 'clerk') && (
            <Button>Schedule New Hearing</Button>
          )}
          <Button variant="outline">Export Schedule</Button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
          <div className="text-red-800">{error}</div>
        </div>
      )}

      {/* Filters */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-lg">Filter Hearings</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <Input
              placeholder="Search hearings..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            
            <select
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={filters.status || ''}
              onChange={(e) => handleFilterChange('status', e.target.value)}
            >
              <option value="">All Statuses</option>
              <option value="scheduled">Scheduled</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="postponed">Postponed</option>
              <option value="cancelled">Cancelled</option>
            </select>

            <select
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={filters.bench_id || ''}
              onChange={(e) => handleFilterChange('bench_id', e.target.value)}
            >
              <option value="">All Benches</option>
              <option value="1">Bench 1</option>
              <option value="2">Bench 2</option>
              <option value="3">Bench 3</option>
            </select>

            <Input
              type="date"
              placeholder="From Date"
              value={filters.date_from || ''}
              onChange={(e) => handleFilterChange('date_from', e.target.value)}
            />

            <Input
              type="date"
              placeholder="To Date"
              value={filters.date_to || ''}
              onChange={(e) => handleFilterChange('date_to', e.target.value)}
            />

            <Button variant="outline" onClick={clearFilters}>
              Clear Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Hearings Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Hearings ({filteredHearings.length})</span>
            <div className="text-sm text-gray-600">
              Total: {hearings.length} hearings
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Hearing ID</TableHead>
                  <TableHead>Case ID</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Time</TableHead>
                  <TableHead>Duration</TableHead>
                  <TableHead>Bench</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Notes</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredHearings.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={9} className="text-center py-8 text-gray-500">
                      No hearings found matching your criteria.
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredHearings.map((hearing) => (
                    <TableRow key={hearing.id}>
                      <TableCell className="font-medium">#{hearing.id}</TableCell>
                      <TableCell>
                        <Button variant="link" className="p-0 h-auto text-blue-600">
                          #{hearing.case_id}
                        </Button>
                      </TableCell>
                      <TableCell>{formatDate(hearing.scheduled_date)}</TableCell>
                      <TableCell>{formatTime(hearing.scheduled_time)}</TableCell>
                      <TableCell>{hearing.duration_minutes} min</TableCell>
                      <TableCell>Bench {hearing.bench_id}</TableCell>
                      <TableCell>
                        <Badge className={getStatusColor(hearing.status)}>
                          {hearing.status.replace('_', ' ').toUpperCase()}
                        </Badge>
                      </TableCell>
                      <TableCell className="max-w-xs truncate" title={hearing.notes}>
                        {hearing.notes}
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button variant="outline" size="sm">
                            View
                          </Button>
                          {(user?.role === 'admin' || user?.role === 'clerk') && (
                            <Button variant="outline" size="sm">
                              Edit
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Today's Schedule Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Today's Hearings</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-600">
              {hearings.filter(h => h.scheduled_date === new Date().toISOString().split('T')[0]).length}
            </div>
            <p className="text-gray-600">Scheduled for today</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Upcoming This Week</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600">
              {hearings.filter(h => h.status === 'scheduled').length}
            </div>
            <p className="text-gray-600">Scheduled hearings</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Completed</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-gray-600">
              {hearings.filter(h => h.status === 'completed').length}
            </div>
            <p className="text-gray-600">This month</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Hearings;
