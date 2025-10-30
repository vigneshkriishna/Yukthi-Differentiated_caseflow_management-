import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Select } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { casesAPI } from '@/services/api'
import toast from 'react-hot-toast'
import { 
  ArrowLeft, 
  Save, 
  Brain, 
  AlertCircle, 
  CheckCircle,
  Sparkles,
  TrendingUp,
  Info
} from 'lucide-react'

interface AIClassification {
  predicted_section: string
  confidence: number
  case_type: string
  suggested_priority: string
  top_predictions: Array<{ section: string; confidence: number }>
}

const NewCase: React.FC = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [aiLoading, setAiLoading] = useState(false)
  const [showAiSuggestion, setShowAiSuggestion] = useState(false)
  const [aiClassification, setAiClassification] = useState<AIClassification | null>(null)

  // Form state
  const [formData, setFormData] = useState({
    case_number: '',
    title: '',
    description: '',
    case_type: '',
    priority: '',
    status: 'filed',
    filing_date: new Date().toISOString().split('T')[0],
    petitioner_name: '',
    respondent_name: '',
    petitioner_lawyer: '',
    respondent_lawyer: '',
    synopsis: ''
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  // AI Classification
  const handleAiClassify = async () => {
    if (!formData.title && !formData.description) {
      toast.error('Please enter case title and description first')
      return
    }

    setAiLoading(true)
    console.log('🤖 Starting AI classification...')
    console.log('Title:', formData.title)
    console.log('Description:', formData.description)
    
    try {
      // Debug: Check ALL localStorage keys
      console.log('🗄️ All localStorage keys:', Object.keys(localStorage))
      console.log('🗄️ localStorage.access_token:', localStorage.getItem('access_token'))
      console.log('🗄️ localStorage.token:', localStorage.getItem('token'))
      console.log('🗄️ localStorage.user:', localStorage.getItem('user'))
      
      const token = localStorage.getItem('access_token')  // Changed from 'token' to 'access_token'
      console.log('🔑 Token exists:', !!token)
      console.log('🔑 Token length:', token?.length)
      console.log('🔑 Token preview:', token?.substring(0, 20) + '...')
      
      if (!token) {
        toast.error('Please login first', {
          icon: '🔒'
        })
        navigate('/login')
        return
      }
      
      console.log('🔍 AI Classification Request:')
      console.log('  URL: http://localhost:8000/api/ai/classify-case')
      console.log('  Title:', formData.title)
      console.log('  Description:', formData.description)
      
      const response = await fetch('http://localhost:8000/api/ai/classify-case', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          title: formData.title,
          description: formData.description
        })
      })

      console.log('Response status:', response.status)
      const data = await response.json()
      console.log('Response data:', data)

      if (response.ok) {
        setAiClassification(data.classification)
        setShowAiSuggestion(true)
        toast.success('AI classification complete!', {
          icon: '🤖',
          duration: 3000
        })
        console.log('✅ AI Classification Success!')
        console.log('📂 Case Type:', data.classification.case_type)
        console.log('🚨 Priority:', data.classification.suggested_priority)
        console.log('💯 Confidence:', (data.classification.confidence * 100).toFixed(1) + '%')
      } else if (response.status === 401) {
        console.error('❌ Authentication failed - token expired or invalid')
        console.log('📋 Full response:', data)
        toast.error('Authentication failed. Token may be expired. Try logging out and back in.', {
          icon: '🔒',
          duration: 5000
        })
        // DON'T redirect - let user stay on the page and try again after re-login
      } else {
        console.error('AI classification failed:', data)
        toast.error(data.detail || 'AI classification failed', {
          duration: 4000
        })
      }
    } catch (error) {
      console.error('AI classification error:', error)
      toast.error('Failed to classify case. Please check your connection.', {
        duration: 4000
      })
    } finally {
      setAiLoading(false)
    }
  }

  // Apply AI suggestions
  const handleApplyAiSuggestions = () => {
    if (!aiClassification) return

    setFormData(prev => ({
      ...prev,
      case_type: aiClassification.case_type.toLowerCase(),
      priority: aiClassification.suggested_priority.toLowerCase()
    }))

    toast.success('AI suggestions applied!', {
      icon: '✅'
    })
  }

  // Submit form
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Validation
    if (!formData.case_number || !formData.title || !formData.description) {
      toast.error('Please fill in all required fields')
      return
    }

    if (!formData.case_type) {
      toast.error('Please select a case type (or use AI to classify)')
      return
    }

    if (!formData.priority) {
      toast.error('Please select a priority (or use AI to suggest)')
      return
    }

    setLoading(true)
    try {
      const caseData = {
        case_number: formData.case_number,
        title: formData.title,
        description: formData.description,
        case_type: formData.case_type as any,
        priority: formData.priority as any,
        status: formData.status as any,
        filing_date: formData.filing_date,
        petitioner_name: formData.petitioner_name,
        respondent_name: formData.respondent_name,
        petitioner_lawyer: formData.petitioner_lawyer,
        respondent_lawyer: formData.respondent_lawyer,
        synopsis: formData.synopsis,
        estimated_duration_minutes: 60
      }
      await casesAPI.create(caseData)
      toast.success('Case created successfully!', {
        icon: '✅'
      })
      navigate('/cases')
    } catch (error: any) {
      console.error('Error creating case:', error)
      toast.error(error.response?.data?.detail || 'Failed to create case')
    } finally {
      setLoading(false)
    }
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600'
    if (confidence >= 0.6) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'urgent': return 'bg-red-100 text-red-800 border-red-300'
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-300'
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-300'
      case 'low': return 'bg-gray-100 text-gray-800 border-gray-300'
      default: return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <Button 
          variant="outline" 
          onClick={() => navigate('/cases')}
          className="flex items-center"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Cases
        </Button>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Create New Case</h1>
          <p className="text-gray-600">Enter case details and use AI for smart classification</p>
        </div>
      </div>

      {/* AI Classification Banner */}
      {showAiSuggestion && aiClassification && (
        <Card className="border-2 border-purple-200 bg-purple-50">
          <CardHeader>
            <CardTitle className="flex items-center text-purple-900">
              <Brain className="h-5 w-5 mr-2" />
              AI Classification Results
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white p-4 rounded-lg border border-purple-200">
                <div className="text-sm text-gray-600 mb-1">Predicted Section</div>
                <div className="font-bold text-lg text-purple-900">
                  {aiClassification.predicted_section}
                </div>
              </div>
              
              <div className="bg-white p-4 rounded-lg border border-purple-200">
                <div className="text-sm text-gray-600 mb-1">Case Type</div>
                <Badge variant="secondary" className="text-sm">
                  {aiClassification.case_type}
                </Badge>
              </div>
              
              <div className="bg-white p-4 rounded-lg border border-purple-200">
                <div className="text-sm text-gray-600 mb-1">Suggested Priority</div>
                <Badge className={getPriorityColor(aiClassification.suggested_priority)}>
                  {aiClassification.suggested_priority.toUpperCase()}
                </Badge>
              </div>
            </div>

            <div className="flex items-center justify-between bg-white p-4 rounded-lg border border-purple-200">
              <div className="flex items-center space-x-2">
                <TrendingUp className={`h-5 w-5 ${getConfidenceColor(aiClassification.confidence)}`} />
                <div>
                  <div className="text-sm text-gray-600">AI Confidence</div>
                  <div className={`font-bold text-lg ${getConfidenceColor(aiClassification.confidence)}`}>
                    {(aiClassification.confidence * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
              
              <Button 
                onClick={handleApplyAiSuggestions}
                className="bg-purple-600 hover:bg-purple-700"
              >
                <CheckCircle className="h-4 w-4 mr-2" />
                Apply AI Suggestions
              </Button>
            </div>

            {aiClassification.confidence < 0.7 && (
              <div className="flex items-start space-x-2 bg-yellow-50 p-3 rounded-lg border border-yellow-200">
                <AlertCircle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                <div className="text-sm text-yellow-800">
                  <strong>Low confidence:</strong> AI is not very confident about this classification. 
                  Please review and adjust manually if needed.
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Main Form */}
      <form onSubmit={handleSubmit}>
        <Card>
          <CardHeader>
            <CardTitle>Case Details</CardTitle>
            <CardDescription>
              Fill in the case information. Required fields are marked with *
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Basic Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="case_number" className="block text-sm font-medium text-gray-700 mb-1">
                  Case Number <span className="text-red-500">*</span>
                </label>
                <Input
                  id="case_number"
                  name="case_number"
                  value={formData.case_number}
                  onChange={handleChange}
                  placeholder="e.g., 2024/001"
                  required
                />
              </div>

              <div>
                <label htmlFor="filing_date">Filing Date</label>
                <Input
                  id="filing_date"
                  name="filing_date"
                  type="date"
                  value={formData.filing_date}
                  onChange={handleChange}
                />
              </div>
            </div>

            {/* Title */}
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
                Case Title <span className="text-red-500">*</span>
              </label>
              <Input
                id="title"
                name="title"
                value={formData.title}
                onChange={handleChange}
                placeholder="e.g., State vs. John Doe - Theft Case"
                required
              />
            </div>

            {/* Description with AI Button */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label htmlFor="description">
                  Case Description <span className="text-red-500">*</span>
                </label>
                <Button
                  type="button"
                  onClick={handleAiClassify}
                  disabled={aiLoading || (!formData.title && !formData.description)}
                  variant="outline"
                  className="border-purple-300 text-purple-700 hover:bg-purple-50"
                >
                  {aiLoading ? (
                    <>
                      <Sparkles className="h-4 w-4 mr-2 animate-spin" />
                      Classifying...
                    </>
                  ) : (
                    <>
                      <Brain className="h-4 w-4 mr-2" />
                      AI Classify
                    </>
                  )}
                </Button>
              </div>
              <Textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                placeholder="Describe the case details, charges, or legal matters..."
                rows={5}
                required
              />
              <p className="text-sm text-gray-500 mt-1">
                <Info className="h-3 w-3 inline mr-1" />
                Click "AI Classify" after entering title and description to get smart priority suggestions
              </p>
            </div>

            {/* Synopsis */}
            <div>
              <label htmlFor="synopsis">Brief Synopsis</label>
              <Textarea
                id="synopsis"
                name="synopsis"
                value={formData.synopsis}
                onChange={handleChange}
                placeholder="One-line summary of the case..."
                rows={2}
              />
            </div>

            {/* Case Type and Priority */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="case_type">
                  Case Type <span className="text-red-500">*</span>
                </label>
                <Select
                  id="case_type"
                  name="case_type"
                  value={formData.case_type}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select type...</option>
                  <option value="criminal">Criminal</option>
                  <option value="civil">Civil</option>
                  <option value="family">Family</option>
                  <option value="commercial">Commercial</option>
                  <option value="constitutional">Constitutional</option>
                </Select>
                {aiClassification && (
                  <p className="text-sm text-purple-600 mt-1">
                    AI suggests: {aiClassification.case_type}
                  </p>
                )}
              </div>

              <div>
                <label htmlFor="priority">
                  Priority <span className="text-red-500">*</span>
                </label>
                <Select
                  id="priority"
                  name="priority"
                  value={formData.priority}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select priority...</option>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </Select>
                {aiClassification && (
                  <p className="text-sm text-purple-600 mt-1">
                    AI suggests: {aiClassification.suggested_priority}
                  </p>
                )}
              </div>
            </div>

            {/* Party Information */}
            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold mb-4">Party Information</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="petitioner_name">Petitioner Name</label>
                  <Input
                    id="petitioner_name"
                    name="petitioner_name"
                    value={formData.petitioner_name}
                    onChange={handleChange}
                    placeholder="Name of petitioner/plaintiff"
                  />
                </div>

                <div>
                  <label htmlFor="petitioner_lawyer">Petitioner Lawyer</label>
                  <Input
                    id="petitioner_lawyer"
                    name="petitioner_lawyer"
                    value={formData.petitioner_lawyer}
                    onChange={handleChange}
                    placeholder="Lawyer representing petitioner"
                  />
                </div>

                <div>
                  <label htmlFor="respondent_name">Respondent Name</label>
                  <Input
                    id="respondent_name"
                    name="respondent_name"
                    value={formData.respondent_name}
                    onChange={handleChange}
                    placeholder="Name of respondent/defendant"
                  />
                </div>

                <div>
                  <label htmlFor="respondent_lawyer">Respondent Lawyer</label>
                  <Input
                    id="respondent_lawyer"
                    name="respondent_lawyer"
                    value={formData.respondent_lawyer}
                    onChange={handleChange}
                    placeholder="Lawyer representing respondent"
                  />
                </div>
              </div>
            </div>

            {/* Status */}
            <div>
              <label htmlFor="status">Initial Status</label>
              <Select
                id="status"
                name="status"
                value={formData.status}
                onChange={handleChange}
              >
                <option value="filed">Filed</option>
                <option value="under_review">Under Review</option>
                <option value="scheduled">Scheduled</option>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="flex items-center justify-end space-x-4 mt-6">
          <Button
            type="button"
            variant="outline"
            onClick={() => navigate('/cases')}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            disabled={loading}
            className="bg-primary hover:bg-primary/90"
          >
            {loading ? (
              <>
                <Sparkles className="h-4 w-4 mr-2 animate-spin" />
                Creating...
              </>
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                Create Case
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  )
}

export default NewCase
