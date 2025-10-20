import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { usePermissions } from '@/contexts/AuthContext'
import { casesAPI } from '@/services/api'
import type { Case } from '@/types'
import toast from 'react-hot-toast'
import { 
  Search, 
  Filter, 
  Plus, 
  Eye, 
  Edit, 
  FileText,
  MoreHorizontal,
  SortAsc,
  SortDesc,
  Upload,
  FolderOpen
} from 'lucide-react'

const Cases: React.FC = () => {
  const [cases, setCases] = useState<Case[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [priorityFilter, setPriorityFilter] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [trackFilter, setTrackFilter] = useState('')
  const [sortBy, setSortBy] = useState('filing_date')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')
  const permissions = usePermissions()

  // Load cases from API
  useEffect(() => {
    loadCases()
  }, [])

  const loadCases = async () => {
    try {
      setLoading(true)
      const response = await casesAPI.getAll()
      setCases(response.data)
    } catch (error: any) {
      toast.error('Failed to load cases')
      console.error('Error loading cases:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'filed': 'bg-blue-100 text-blue-800',
      'under_review': 'bg-yellow-100 text-yellow-800',
      'scheduled': 'bg-purple-100 text-purple-800',
      'hearing': 'bg-indigo-100 text-indigo-800',
      'judgment_reserved': 'bg-orange-100 text-orange-800',
      'disposed': 'bg-green-100 text-green-800',
      'appealed': 'bg-red-100 text-red-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      'low': 'bg-gray-100 text-gray-800',
      'medium': 'bg-yellow-100 text-yellow-800',
      'high': 'bg-orange-100 text-orange-800',
      'urgent': 'bg-red-100 text-red-800'
    }
    return colors[priority] || 'bg-gray-100 text-gray-800'
  }

  const getTrackColor = (track: string) => {
    const colors: Record<string, string> = {
      'fast': 'bg-green-100 text-green-800',
      'regular': 'bg-blue-100 text-blue-800',
      'complex': 'bg-purple-100 text-purple-800'
    }
    return colors[track] || 'bg-gray-100 text-gray-800'
  }

  const getCaseTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      'criminal': 'bg-red-100 text-red-800',
      'civil': 'bg-blue-100 text-blue-800',
      'family': 'bg-pink-100 text-pink-800',
      'commercial': 'bg-green-100 text-green-800',
      'constitutional': 'bg-purple-100 text-purple-800'
    }
    return colors[type] || 'bg-gray-100 text-gray-800'
  }

  const handleSort = (column: string) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(column)
      setSortOrder('asc')
    }
  }

  // Filter and sort cases
  const filteredCases = cases
    .filter(case_ => {
      const matchesSearch = !searchTerm || 
        case_.case_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
        case_.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        case_.synopsis.toLowerCase().includes(searchTerm.toLowerCase())
      
      const matchesStatus = !statusFilter || case_.status === statusFilter
      const matchesPriority = !priorityFilter || case_.priority === priorityFilter
      const matchesType = !typeFilter || case_.case_type === typeFilter
      const matchesTrack = !trackFilter || case_.track === trackFilter

      return matchesSearch && matchesStatus && matchesPriority && matchesType && matchesTrack
    })
    .sort((a, b) => {
      const aVal = a[sortBy as keyof Case]
      const bVal = b[sortBy as keyof Case]
      
      if (aVal === null || aVal === undefined) return 1
      if (bVal === null || bVal === undefined) return -1
      
      if (sortOrder === 'asc') {
        return aVal < bVal ? -1 : aVal > bVal ? 1 : 0
      } else {
        return aVal > bVal ? -1 : aVal < bVal ? 1 : 0
      }
    })

  const SortIcon = ({ column }: { column: string }) => {
    if (sortBy !== column) return null
    return sortOrder === 'asc' ? <SortAsc className="h-4 w-4" /> : <SortDesc className="h-4 w-4" />
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Cases</h1>
          <p className="text-gray-600">Manage and track all legal cases</p>
        </div>
        {permissions.canCreate('cases') && (
          <Button>
            <Link to="/cases/new" className="flex items-center">
              <Plus className="h-4 w-4 mr-2" />
              New Case
            </Link>
          </Button>
        )}
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Filter className="h-5 w-5 mr-2" />
            Filters & Search
          </CardTitle>
          <CardDescription>
            Filter and search cases by various criteria
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
            {/* Search */}
            <div className="lg:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Search
              </label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search cases..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Status Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <Select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
                <option value="">All Statuses</option>
                <option value="filed">Filed</option>
                <option value="under_review">Under Review</option>
                <option value="scheduled">Scheduled</option>
                <option value="hearing">Hearing</option>
                <option value="judgment_reserved">Judgment Reserved</option>
                <option value="disposed">Disposed</option>
                <option value="appealed">Appealed</option>
              </Select>
            </div>

            {/* Priority Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Priority
              </label>
              <Select value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)}>
                <option value="">All Priorities</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </Select>
            </div>

            {/* Type Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Type
              </label>
              <Select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
                <option value="">All Types</option>
                <option value="criminal">Criminal</option>
                <option value="civil">Civil</option>
                <option value="family">Family</option>
                <option value="commercial">Commercial</option>
                <option value="constitutional">Constitutional</option>
              </Select>
            </div>

            {/* Track Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Track
              </label>
              <Select value={trackFilter} onChange={(e) => setTrackFilter(e.target.value)}>
                <option value="">All Tracks</option>
                <option value="fast">Fast Track</option>
                <option value="regular">Regular</option>
                <option value="complex">Complex</option>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Cases Table */}
      <Card>
        <CardHeader>
          <CardTitle>
            Cases ({filteredCases.length})
          </CardTitle>
          <CardDescription>
            List of all cases matching your filters
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">
              <div className="text-lg text-gray-600">Loading cases...</div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
              <TableHeader>
                <TableRow>
                  <TableHead 
                    className="cursor-pointer hover:bg-gray-50"
                    onClick={() => handleSort('case_number')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>Case Number</span>
                      <SortIcon column="case_number" />
                    </div>
                  </TableHead>
                  <TableHead 
                    className="cursor-pointer hover:bg-gray-50"
                    onClick={() => handleSort('title')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>Title</span>
                      <SortIcon column="title" />
                    </div>
                  </TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Priority</TableHead>
                  <TableHead>Track</TableHead>
                  <TableHead 
                    className="cursor-pointer hover:bg-gray-50"
                    onClick={() => handleSort('filing_date')}
                  >
                    <div className="flex items-center space-x-1">
                      <span>Filed Date</span>
                      <SortIcon column="filing_date" />
                    </div>
                  </TableHead>
                  <TableHead>Next Hearing</TableHead>
                  <TableHead>Judge</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredCases.map((case_) => (
                  <TableRow key={case_.id}>
                    <TableCell className="font-medium">
                      <Link 
                        to={`/cases/${case_.id}`}
                        className="text-primary hover:underline"
                      >
                        {case_.case_number}
                      </Link>
                    </TableCell>
                    <TableCell>
                      <div>
                        <div className="font-medium">{case_.title}</div>
                        <div className="text-sm text-gray-500">
                          {case_.synopsis}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge className={getCaseTypeColor(case_.case_type)}>
                        {case_.case_type}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge className={getStatusColor(case_.status)}>
                        {case_.status.replace('_', ' ')}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge className={getPriorityColor(case_.priority)}>
                        {case_.priority}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge className={getTrackColor(case_.track || 'REGULAR')}>
                        {case_.track || 'Not Classified'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {new Date(case_.filing_date).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <span className="text-gray-400">No hearing scheduled</span>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">-</div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        <Button variant="ghost" size="sm" title="View case">
                          <Link to={`/cases/${case_.id}`}>
                            <Eye className="h-4 w-4" />
                          </Link>
                        </Button>
                        {permissions.canUpdate('cases') && (
                          <Button variant="ghost" size="sm" title="Edit case">
                            <Link to={`/cases/${case_.id}/edit`}>
                              <Edit className="h-4 w-4" />
                            </Link>
                          </Button>
                        )}
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          title="Upload documents for this case"
                          onClick={() => window.open(`/documents?caseId=${case_.id}&tab=upload`, '_blank')}
                        >
                          <Upload className="h-4 w-4" />
                        </Button>
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          title="View case documents"
                          onClick={() => window.open(`/documents?caseId=${case_.id}`, '_blank')}
                        >
                          <FolderOpen className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          )}

          {!loading && filteredCases.length === 0 && (
            <div className="text-center py-8">
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No cases found</h3>
              <p className="text-gray-500 mb-4">
                No cases match your current filters. Try adjusting your search criteria.
              </p>
              {permissions.canCreate('cases') && (
                <Button>
                  <Link to="/cases/new">
                    <Plus className="h-4 w-4 mr-2" />
                    Create New Case
                  </Link>
                </Button>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default Cases
