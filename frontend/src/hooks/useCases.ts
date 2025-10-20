import { useQuery, useMutation, useQueryClient } from 'react-query'
import { api } from '@/services/api'
import { Case, CaseFilters, CreateCaseRequest, UpdateCaseRequest, CaseListResponse } from '@/types'

// Query keys
export const caseKeys = {
  all: ['cases'] as const,
  lists: () => [...caseKeys.all, 'list'] as const,
  list: (filters: CaseFilters) => [...caseKeys.lists(), filters] as const,
  details: () => [...caseKeys.all, 'detail'] as const,
  detail: (id: number) => [...caseKeys.details(), id] as const,
  search: (query: string) => [...caseKeys.all, 'search', query] as const,
  stats: () => [...caseKeys.all, 'stats'] as const,
}

// Fetch cases with filters
export const useCases = (filters: CaseFilters = {}) => {
  return useQuery({
    queryKey: caseKeys.list(filters),
    queryFn: async (): Promise<CaseListResponse> => {
      const params = new URLSearchParams()
      
      if (filters.status) params.append('status', filters.status)
      if (filters.priority) params.append('priority', filters.priority)
      if (filters.track) params.append('track', filters.track)
      if (filters.case_type) params.append('case_type', filters.case_type)
      if (filters.judge_id) params.append('judge_id', filters.judge_id.toString())
      if (filters.search) params.append('search', filters.search)
      if (filters.skip !== undefined) params.append('skip', filters.skip.toString())
      if (filters.limit !== undefined) params.append('limit', filters.limit.toString())
      if (filters.sort_by) params.append('sort_by', filters.sort_by)
      if (filters.sort_order) params.append('sort_order', filters.sort_order)

      const response = await api.get(`/cases?${params.toString()}`)
      return response.data
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Fetch single case
export const useCase = (id: number) => {
  return useQuery({
    queryKey: caseKeys.detail(id),
    queryFn: async (): Promise<Case> => {
      const response = await api.get(`/cases/${id}`)
      return response.data
    },
    enabled: !!id,
  })
}

// Search cases
export const useCaseSearch = (query: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: caseKeys.search(query),
    queryFn: async (): Promise<Case[]> => {
      if (!query.trim()) return []
      
      const response = await api.get(`/cases/search?q=${encodeURIComponent(query)}`)
      return response.data
    },
    enabled: enabled && !!query.trim(),
    staleTime: 30 * 1000, // 30 seconds
  })
}

// Case statistics
export const useCaseStats = () => {
  return useQuery({
    queryKey: caseKeys.stats(),
    queryFn: async () => {
      const response = await api.get('/cases/stats')
      return response.data
    },
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}

// Create case mutation
export const useCreateCase = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: CreateCaseRequest): Promise<Case> => {
      const response = await api.post('/cases', data)
      return response.data
    },
    onSuccess: (newCase) => {
      // Invalidate and refetch cases list
      queryClient.invalidateQueries({ queryKey: caseKeys.lists() })
      queryClient.invalidateQueries({ queryKey: caseKeys.stats() })
      
      // Add to cache
      queryClient.setQueryData(caseKeys.detail(newCase.id), newCase)
    },
  })
}

// Update case mutation
export const useUpdateCase = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: UpdateCaseRequest }): Promise<Case> => {
      const response = await api.put(`/cases/${id}`, data)
      return response.data
    },
    onSuccess: (updatedCase) => {
      // Update cache
      queryClient.setQueryData(caseKeys.detail(updatedCase.id), updatedCase)
      
      // Invalidate lists to reflect changes
      queryClient.invalidateQueries({ queryKey: caseKeys.lists() })
      queryClient.invalidateQueries({ queryKey: caseKeys.stats() })
    },
  })
}

// Delete case mutation
export const useDeleteCase = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (id: number): Promise<void> => {
      await api.delete(`/cases/${id}`)
    },
    onSuccess: (_, id) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: caseKeys.detail(id) })
      
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: caseKeys.lists() })
      queryClient.invalidateQueries({ queryKey: caseKeys.stats() })
    },
  })
}

// Assign case to judge mutation
export const useAssignCase = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ caseId, judgeId }: { caseId: number; judgeId: number }): Promise<Case> => {
      const response = await api.post(`/cases/${caseId}/assign`, { judge_id: judgeId })
      return response.data
    },
    onSuccess: (updatedCase) => {
      queryClient.setQueryData(caseKeys.detail(updatedCase.id), updatedCase)
      queryClient.invalidateQueries({ queryKey: caseKeys.lists() })
    },
  })
}

// Update case status mutation
export const useUpdateCaseStatus = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, status }: { id: number; status: string }): Promise<Case> => {
      const response = await api.patch(`/cases/${id}/status`, { status })
      return response.data
    },
    onSuccess: (updatedCase) => {
      queryClient.setQueryData(caseKeys.detail(updatedCase.id), updatedCase)
      queryClient.invalidateQueries({ queryKey: caseKeys.lists() })
      queryClient.invalidateQueries({ queryKey: caseKeys.stats() })
    },
  })
}

// Update case priority mutation
export const useUpdateCasePriority = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, priority }: { id: number; priority: string }): Promise<Case> => {
      const response = await api.patch(`/cases/${id}/priority`, { priority })
      return response.data
    },
    onSuccess: (updatedCase) => {
      queryClient.setQueryData(caseKeys.detail(updatedCase.id), updatedCase)
      queryClient.invalidateQueries({ queryKey: caseKeys.lists() })
    },
  })
}

// Override case track mutation
export const useOverrideCaseTrack = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, track }: { id: number; track: string }): Promise<Case> => {
      const response = await api.patch(`/cases/${id}/track`, { track })
      return response.data
    },
    onSuccess: (updatedCase) => {
      queryClient.setQueryData(caseKeys.detail(updatedCase.id), updatedCase)
      queryClient.invalidateQueries({ queryKey: caseKeys.lists() })
    },
  })
}

// Add case note mutation
export const useAddCaseNote = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ caseId, note }: { caseId: number; note: string }): Promise<Case> => {
      const response = await api.post(`/cases/${caseId}/notes`, { content: note })
      return response.data
    },
    onSuccess: (updatedCase) => {
      queryClient.setQueryData(caseKeys.detail(updatedCase.id), updatedCase)
    },
  })
}

// Upload case document mutation
export const useUploadCaseDocument = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ caseId, file, title, documentType }: {
      caseId: number
      file: File
      title: string
      documentType: string
    }): Promise<Case> => {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('title', title)
      formData.append('document_type', documentType)

      const response = await api.post(`/cases/${caseId}/documents`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      return response.data
    },
    onSuccess: (updatedCase) => {
      queryClient.setQueryData(caseKeys.detail(updatedCase.id), updatedCase)
    },
  })
}

// Bulk update cases mutation
export const useBulkUpdateCases = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ caseIds, updates }: {
      caseIds: number[]
      updates: Partial<UpdateCaseRequest>
    }): Promise<Case[]> => {
      const response = await api.patch('/cases/bulk', {
        case_ids: caseIds,
        updates,
      })
      return response.data
    },
    onSuccess: () => {
      // Invalidate all case-related queries since multiple cases were updated
      queryClient.invalidateQueries({ queryKey: caseKeys.all })
    },
  })
}
