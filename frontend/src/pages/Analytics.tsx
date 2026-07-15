import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  Chip,
} from '@mui/material';
import {
  Assessment as AssessmentIcon,
  TrendingUp as TrendingUpIcon,
  Speed as SpeedIcon,
  Psychology as PsychologyIcon,
  Lightbulb as LightbulbIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import { analyticsAPI, competitorsAPI } from '../services/api';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box>{children}</Box>}
    </div>
  );
}

export default function Analytics() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [tabValue, setTabValue] = useState(0);
  const [competitors, setCompetitors] = useState<any[]>([]);
  const [swotData, setSwotData] = useState<any[]>([]);
  const [insights, setInsights] = useState<any[]>([]);

  useEffect(() => {
    loadAnalyticsData();
  }, []);

  const loadAnalyticsData = async () => {
    try {
      setLoading(true);

      // Load competitors
      const competitorsResponse = await competitorsAPI.list();
      setCompetitors(competitorsResponse.data || []);

      // Load insights
      const insightsResponse = await analyticsAPI.insights();
      setInsights(insightsResponse.data || []);

      // Mock SWOT data
      setSwotData([
        { subject: 'Market Share', A: 85, B: 70, fullMark: 100 },
        { subject: 'Brand Recognition', A: 75, B: 80, fullMark: 100 },
        { subject: 'Product Quality', A: 90, B: 75, fullMark: 100 },
        { subject: 'Customer Service', A: 80, B: 70, fullMark: 100 },
        { subject: 'Innovation', A: 85, B: 65, fullMark: 100 },
        { subject: 'Pricing', A: 70, B: 85, fullMark: 100 },
        { subject: 'Distribution', A: 75, B: 70, fullMark: 100 },
      ]);

    } catch (err: any) {
      setError('Failed to load analytics data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Analytics
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Deep insights and competitive analysis
          </Typography>
        </Box>
        <Button variant="contained" startIcon={<AssessmentIcon />}>
          Generate Report
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Quick Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {[
          { title: 'Competitive Score', value: '82/100', change: '+5', icon: <SpeedIcon />, color: '#1976d2' },
          { title: 'Market Position', value: '#3', change: '+1', icon: <TrendingUpIcon />, color: '#2e7d32' },
          { title: 'Growth Potential', value: 'High', change: 'Stable', icon: <PsychologyIcon />, color: '#ed6c02' },
          { title: 'Risk Level', value: 'Medium', change: '-2', icon: <WarningIcon />, color: '#c62828' },
        ].map((stat) => (
          <Grid item xs={12} sm={6} md={3} key={stat.title}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box>
                    <Typography color="text.secondary" variant="body2" gutterBottom>
                      {stat.title}
                    </Typography>
                    <Typography variant="h4" component="div" sx={{ color: stat.color }}>
                      {stat.value}
                    </Typography>
                    <Typography variant="caption" sx={{ color: stat.color }}>
                      {stat.change}
                    </Typography>
                  </Box>
                  <Box sx={{ color: stat.color, fontSize: 32 }}>
                    {stat.icon}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
          <Tab label="SWOT Analysis" />
          <Tab label="Competitor Comparison" />
          <Tab label="Insights & Recommendations" />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Strengths
                </Typography>
                {[
                  'Strong brand recognition in target market',
                  'Superior product quality and reliability',
                  'Loyal customer base with high retention',
                  'Advanced technology infrastructure',
                  'Experienced leadership team',
                ].map((item, index) => (
                  <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <LightbulbIcon sx={{ color: '#2e7d32', fontSize: 20 }} />
                    <Typography variant="body2">{item}</Typography>
                  </Box>
                ))}
              </CardContent>
            </Card>

            <Card sx={{ mt: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Opportunities
                </Typography>
                {[
                  'Expanding into emerging markets',
                  'Strategic partnerships and acquisitions',
                  'New product line development',
                  'Digital transformation initiatives',
                  'Sustainability and ESG focus',
                ].map((item, index) => (
                  <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <TrendingUpIcon sx={{ color: '#1976d2', fontSize: 20 }} />
                    <Typography variant="body2">{item}</Typography>
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Weaknesses
                </Typography>
                {[
                  'Limited market presence in certain regions',
                  'Higher pricing compared to competitors',
                  'Slower time-to-market for new features',
                  'Dependency on key suppliers',
                  'Limited marketing budget',
                ].map((item, index) => (
                  <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <WarningIcon sx={{ color: '#ed6c02', fontSize: 20 }} />
                    <Typography variant="body2">{item}</Typography>
                  </Box>
                ))}
              </CardContent>
            </Card>

            <Card sx={{ mt: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Threats
                </Typography>
                {[
                  'Increasing competition from new entrants',
                  'Regulatory changes in key markets',
                  'Economic uncertainty affecting demand',
                  'Rapid technological changes',
                  'Supply chain disruptions',
                ].map((item, index) => (
                  <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <WarningIcon sx={{ color: '#c62828', fontSize: 20 }} />
                    <Typography variant="body2">{item}</Typography>
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Competitive Position Analysis
                </Typography>
                <ResponsiveContainer width="100%" height={400}>
                  <RadarChart data={swotData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="subject" />
                    <PolarRadiusAxis angle={90} domain={[0, 100]} />
                    <Radar name="Your Company" dataKey="A" stroke="#1976d2" fill="#1976d2" fillOpacity={0.6} />
                    <Radar name="Market Average" dataKey="B" stroke="#dc004e" fill="#dc004e" fillOpacity={0.6} />
                    <Tooltip />
                  </RadarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Competitor Performance Comparison
                </Typography>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={[
                    { competitor: 'Your Company', revenue: 120, growth: 15, marketShare: 18 },
                    { competitor: 'Competitor A', revenue: 150, growth: 12, marketShare: 22 },
                    { competitor: 'Competitor B', revenue: 90, growth: 18, marketShare: 14 },
                    { competitor: 'Competitor C', revenue: 110, growth: 10, marketShare: 16 },
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="competitor" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="revenue" fill="#1976d2" name="Revenue ($M)" />
                    <Bar dataKey="growth" fill="#2e7d32" name="Growth (%)" />
                    <Bar dataKey="marketShare" fill="#ed6c02" name="Market Share (%)" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Performance Metrics
                </Typography>
                {[
                  { metric: 'Revenue Growth', your: '15%', avg: '12%', status: 'above' },
                  { metric: 'Customer Satisfaction', your: '4.5/5', avg: '4.2/5', status: 'above' },
                  { metric: 'Market Share', your: '18%', avg: '15%', status: 'above' },
                  { metric: 'Brand Recognition', your: '72%', avg: '68%', status: 'above' },
                  { metric: 'Innovation Index', your: '8.2/10', avg: '7.5/10', status: 'above' },
                ].map((item, index) => (
                  <Box key={index} sx={{ py: 1, borderBottom: index < 4 ? 1 : 0, borderColor: 'divider' }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2">{item.metric}</Typography>
                      <Chip
                        label={item.status === 'above' ? 'Above Average' : 'Below Average'}
                        color={item.status === 'above' ? 'success' : 'error'}
                        size="small"
                      />
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 0.5 }}>
                      <Typography variant="h6" color="#1976d2">{item.your}</Typography>
                      <Typography variant="body2" color="text.secondary">Avg: {item.avg}</Typography>
                    </Box>
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Competitive Advantages
                </Typography>
                {[
                  { advantage: 'Technology Leadership', gap: 'High', sustainability: 'Long-term' },
                  { advantage: 'Customer Relationships', gap: 'Medium', sustainability: 'Long-term' },
                  { advantage: 'Brand Strength', gap: 'Medium', sustainability: 'Medium-term' },
                  { advantage: 'Cost Structure', gap: 'Low', sustainability: 'Short-term' },
                  { advantage: 'Distribution Network', gap: 'High', sustainability: 'Long-term' },
                ].map((item, index) => (
                  <Box key={index} sx={{ py: 1, borderBottom: index < 4 ? 1 : 0, borderColor: 'divider' }}>
                    <Typography variant="body2" fontWeight="medium">
                      {item.advantage}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                      <Chip label={`Gap: ${item.gap}`} size="small" variant="outlined" />
                      <Chip label={item.sustainability} size="small" variant="outlined" />
                    </Box>
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <Grid container spacing={3}>
          {[
            {
              type: 'opportunity',
              title: 'Expand into Asia-Pacific Market',
              description: 'Market analysis shows significant growth potential in APAC region with low competitive saturation.',
              impact: 'high',
              effort: 'medium',
              priority: '1',
            },
            {
              type: 'opportunity',
              title: 'Launch Premium Product Line',
              description: 'Customer feedback indicates willingness to pay premium for enhanced features and support.',
              impact: 'high',
              effort: 'high',
              priority: '2',
            },
            {
              type: 'risk',
              title: 'Competitor Price War Threat',
              description: 'Intelligence suggests Competitor A may launch aggressive pricing strategy in Q3.',
              impact: 'high',
              effort: 'high',
              priority: '1',
            },
            {
              type: 'opportunity',
              title: 'Strategic Partnership Opportunity',
              description: 'Potential partnership with Industry Leader X could expand market reach significantly.',
              impact: 'medium',
              effort: 'low',
              priority: '3',
            },
            {
              type: 'risk',
              title: 'Regulatory Compliance Update',
              description: 'New data privacy regulations may require updates to data handling processes.',
              impact: 'medium',
              effort: 'medium',
              priority: '2',
            },
            {
              type: 'opportunity',
              title: 'AI-Powered Feature Integration',
              description: 'Leveraging AI capabilities could differentiate product offering and improve customer experience.',
              impact: 'medium',
              effort: 'high',
              priority: '4',
            },
          ].map((insight, index) => (
            <Grid item xs={12} md={6} key={index}>
              <Card sx={{
                borderLeft: 4,
                borderColor: insight.type === 'opportunity' ? '#2e7d32' : '#c62828',
              }}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {insight.type === 'opportunity' ? (
                        <LightbulbIcon sx={{ color: '#2e7d32' }} />
                      ) : (
                        <WarningIcon sx={{ color: '#c62828' }} />
                      )}
                      <Typography variant="subtitle1" fontWeight="medium">
                        {insight.title}
                      </Typography>
                    </Box>
                    <Chip
                      label={`Priority ${insight.priority}`}
                      color={parseInt(insight.priority) <= 2 ? 'error' : 'default'}
                      size="small"
                    />
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1, mb: 2 }}>
                    {insight.description}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Chip label={`Impact: ${insight.impact}`} size="small" variant="outlined" />
                    <Chip label={`Effort: ${insight.effort}`} size="small" variant="outlined" />
                    <Chip
                      label={insight.type === 'opportunity' ? 'Opportunity' : 'Risk'}
                      color={insight.type === 'opportunity' ? 'success' : 'error'}
                      size="small"
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </TabPanel>
    </Box>
  );
}