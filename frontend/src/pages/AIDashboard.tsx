import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { 
  Brain, 
  FileText, 
  Search, 
  Lightbulb, 
  TrendingUp, 
  Zap,
  BookOpen,
  Target,
  CheckCircle
} from 'lucide-react';

interface AIAnalytics {
  total_cases_analyzed: number;
  classification_accuracy: string;
  top_case_types: Array<{ type: string; count: number }>;
  priority_distribution: Record<string, number>;
  recent_ai_activities: string[];
  model_info: any;
}

interface Classification {
  predicted_section: string;
  confidence: number;
  case_type: string;
  suggested_priority: string;
  top_predictions: Array<{ section: string; confidence: number }>;
}

const AIDashboard: React.FC = () => {
  const [analytics, setAnalytics] = useState<AIAnalytics | null>(null);
  // Removed unused loading state
  
  // Case Classification Demo
  const [classificationInput, setClassificationInput] = useState({
    title: '',
    description: ''
  });
  const [classification, setClassification] = useState<Classification | null>(null);
  const [classifyLoading, setClassifyLoading] = useState(false);

  // Document Analysis Demo
  const [documentContent, setDocumentContent] = useState('');
  const [documentAnalysis, setDocumentAnalysis] = useState<any>(null);
  const [analyzeLoading, setAnalyzeLoading] = useState(false);

  // Similar Cases Demo
  const [similarCasesQuery, setSimilarCasesQuery] = useState({
    title: '',
    description: ''
  });
  const [similarCases, setSimilarCases] = useState<any[]>([]);
  const [similarLoading, setSimilarLoading] = useState(false);

  // Load AI analytics on component mount
  useEffect(() => {
    loadAIAnalytics();
  }, []);

  const getAuthHeaders = () => {
    const token = localStorage.getItem('access_token');  // Fixed: Changed from 'token' to 'access_token'
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  };

  const loadAIAnalytics = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/ai/dashboard-analytics', {
        headers: getAuthHeaders()
      });

      if (response.ok) {
        const data = await response.json();
        setAnalytics(data.analytics);
      }
    } catch (error) {
      console.error('Error loading AI analytics:', error);
    }
  };

  const classifyCase = async () => {
    if (!classificationInput.title && !classificationInput.description) return;
    
    setClassifyLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/ai/classify-case', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(classificationInput)
      });

      if (response.ok) {
        const data = await response.json();
        setClassification(data.classification);
      }
    } catch (error) {
      console.error('Error classifying case:', error);
    } finally {
      setClassifyLoading(false);
    }
  };

  const analyzeDocument = async () => {
    if (!documentContent.trim()) return;
    
    setAnalyzeLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/ai/analyze-document', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          content: documentContent,
          filename: 'demo-document.txt'
        })
      });

      if (response.ok) {
        const data = await response.json();
        setDocumentAnalysis(data.analysis);
      }
    } catch (error) {
      console.error('Error analyzing document:', error);
    } finally {
      setAnalyzeLoading(false);
    }
  };

  const findSimilarCases = async () => {
    if (!similarCasesQuery.title && !similarCasesQuery.description) return;
    
    setSimilarLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/ai/similar-cases', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(similarCasesQuery)
      });

      if (response.ok) {
        const data = await response.json();
        setSimilarCases(data.similar_cases);
      }
    } catch (error) {
      console.error('Error finding similar cases:', error);
    } finally {
      setSimilarLoading(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-2">
        <Brain className="h-8 w-8 text-purple-600" />
        <h1 className="text-3xl font-bold">AI-Powered Legal Analytics</h1>
      </div>

      <div className="text-sm text-gray-600 bg-blue-50 p-4 rounded-lg border-l-4 border-blue-400">
        <div className="flex items-center space-x-2">
          <Zap className="h-5 w-5 text-blue-600" />
          <span className="font-semibold">AI Features Active:</span>
        </div>
        <p className="mt-1">
          Advanced machine learning models are analyzing your legal cases, documents, and providing intelligent insights.
        </p>
      </div>

      {/* AI Analytics Overview */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Cases Analyzed</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{analytics.total_cases_analyzed}</div>
              <p className="text-xs text-muted-foreground">
                AI classification active
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Classification Accuracy</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{analytics.classification_accuracy}</div>
              <p className="text-xs text-muted-foreground">
                Model performance
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Top Case Type</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {analytics.top_case_types[0]?.type || 'N/A'}
              </div>
              <p className="text-xs text-muted-foreground">
                {analytics.top_case_types[0]?.count || 0} cases
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">AI Features</CardTitle>
              <Brain className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-600">6+</div>
              <p className="text-xs text-muted-foreground">
                Active AI capabilities
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* AI Demo Features - Part 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Case Classification */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Brain className="h-5 w-5 text-purple-600" />
              <span>Smart Case Classification</span>
            </CardTitle>
            <CardDescription>
              Automatically classify cases using advanced NLP and the BNS legal framework
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium">Case Title</label>
              <Input
                placeholder="e.g., State vs. Johnson - Theft Case"
                value={classificationInput.title}
                onChange={(e) => setClassificationInput({
                  ...classificationInput,
                  title: e.target.value
                })}
              />
            </div>
            <div>
              <label className="text-sm font-medium">Case Description</label>
              <Textarea
                placeholder="Describe the case details, charges, or civil matter..."
                value={classificationInput.description}
                onChange={(e) => setClassificationInput({
                  ...classificationInput,
                  description: e.target.value
                })}
                rows={3}
              />
            </div>
            <Button 
              onClick={classifyCase}
              disabled={classifyLoading}
              className="w-full"
            >
              {classifyLoading ? 'Analyzing...' : 'Classify Case'}
            </Button>

            {classification && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <h4 className="font-semibold mb-2">Classification Results:</h4>
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span>Predicted Section:</span>
                    <Badge variant="secondary">{classification.predicted_section}</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Case Type:</span>
                    <Badge variant="outline">{classification.case_type}</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Suggested Priority:</span>
                    <Badge className={getPriorityColor(classification.suggested_priority)}>
                      {classification.suggested_priority}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>Confidence:</span>
                    <span className={`font-bold ${getConfidenceColor(classification.confidence)}`}>
                      {(classification.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Document Analysis */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <FileText className="h-5 w-5 text-blue-600" />
              <span>Document Analysis</span>
            </CardTitle>
            <CardDescription>
              Extract key information, entities, and insights from legal documents
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium">Document Content</label>
              <Textarea
                placeholder="Paste document content here for AI analysis..."
                value={documentContent}
                onChange={(e) => setDocumentContent(e.target.value)}
                rows={4}
              />
            </div>
            <Button 
              onClick={analyzeDocument}
              disabled={analyzeLoading}
              className="w-full"
            >
              {analyzeLoading ? 'Analyzing...' : 'Analyze Document'}
            </Button>

            {documentAnalysis && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg max-h-60 overflow-y-auto">
                <h4 className="font-semibold mb-2">Analysis Results:</h4>
                <div className="space-y-2 text-sm">
                  <div><strong>Document Type:</strong> {documentAnalysis.document_type}</div>
                  <div><strong>Word Count:</strong> {documentAnalysis.word_count}</div>
                  <div><strong>Sentiment:</strong> {documentAnalysis.sentiment}</div>
                  {documentAnalysis.key_entities?.length > 0 && (
                    <div>
                      <strong>Key Entities:</strong>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {documentAnalysis.key_entities.slice(0, 5).map((entity: any, index: number) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {entity.type}: {entity.value}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                  {documentAnalysis.summary && (
                    <div>
                      <strong>Summary:</strong>
                      <p className="mt-1 text-gray-700">{documentAnalysis.summary}</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* AI Demo Features - Part 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Similar Cases Search */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Search className="h-5 w-5 text-green-600" />
              <span>Similar Cases Finder</span>
            </CardTitle>
            <CardDescription>
              Find cases with similar legal issues, facts, or precedents
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium">Case Title</label>
              <Input
                placeholder="e.g., Property Dispute Case"
                value={similarCasesQuery.title}
                onChange={(e) => setSimilarCasesQuery({
                  ...similarCasesQuery,
                  title: e.target.value
                })}
              />
            </div>
            <div>
              <label className="text-sm font-medium">Case Description</label>
              <Textarea
                placeholder="Describe the case you want to find similar cases for..."
                value={similarCasesQuery.description}
                onChange={(e) => setSimilarCasesQuery({
                  ...similarCasesQuery,
                  description: e.target.value
                })}
                rows={3}
              />
            </div>
            <Button 
              onClick={findSimilarCases}
              disabled={similarLoading}
              className="w-full"
            >
              {similarLoading ? 'Searching...' : 'Find Similar Cases'}
            </Button>

            {similarCases.length > 0 && (
              <div className="mt-4 space-y-2">
                <h4 className="font-semibold">Similar Cases Found:</h4>
                {similarCases.map((case_item, index) => (
                  <div key={index} className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h5 className="font-medium">{case_item.case_number}</h5>
                        <p className="text-sm text-gray-600">{case_item.title}</p>
                        <div className="flex items-center space-x-2 mt-1">
                          <Badge variant="outline" className="text-xs">
                            {case_item.case_type}
                          </Badge>
                          <Badge variant="secondary" className="text-xs">
                            {(case_item.similarity_score * 100).toFixed(0)}% match
                          </Badge>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* AI Insights */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Lightbulb className="h-5 w-5 text-yellow-600" />
              <span>AI Recent Activities</span>
            </CardTitle>
            <CardDescription>
              Latest AI-powered insights and activities in your system
            </CardDescription>
          </CardHeader>
          <CardContent>
            {analytics?.recent_ai_activities && (
              <div className="space-y-3">
                {analytics.recent_ai_activities.map((activity, index) => (
                  <div key={index} className="flex items-center space-x-3 p-2 bg-gray-50 rounded-lg">
                    <CheckCircle className="h-4 w-4 text-green-500 flex-shrink-0" />
                    <span className="text-sm">{activity}</span>
                  </div>
                ))}
              </div>
            )}

            <div className="mt-4 pt-4 border-t">
              <h5 className="font-semibold mb-2 flex items-center space-x-2">
                <BookOpen className="h-4 w-4" />
                <span>Model Information</span>
              </h5>
              <div className="text-sm text-gray-600 space-y-1">
                <div>Enhanced BNS Legal Classifier</div>
                <div>Version: 3.0 (AI-Powered)</div>
                <div>Last Updated: {new Date().toLocaleDateString()}</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Zap className="h-5 w-5 text-purple-600" />
            <span>Quick AI Actions</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button variant="outline" className="p-4 h-auto flex flex-col items-center space-y-2">
              <Brain className="h-6 w-6 text-purple-600" />
              <span className="font-semibold">Bulk Case Classification</span>
              <span className="text-xs text-gray-500">Classify multiple cases at once</span>
            </Button>
            
            <Button variant="outline" className="p-4 h-auto flex flex-col items-center space-y-2">
              <FileText className="h-6 w-6 text-blue-600" />
              <span className="font-semibold">Document Batch Analysis</span>
              <span className="text-xs text-gray-500">Analyze multiple documents</span>
            </Button>
            
            <Button variant="outline" className="p-4 h-auto flex flex-col items-center space-y-2">
              <TrendingUp className="h-6 w-6 text-green-600" />
              <span className="font-semibold">Generate AI Report</span>
              <span className="text-xs text-gray-500">Comprehensive AI insights</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AIDashboard;