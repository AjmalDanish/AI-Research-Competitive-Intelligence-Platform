import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  Chip,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  AutoGraph as AutoGraphIcon,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar } from 'recharts';


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

export default function MarketIntelligence() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [tabValue, setTabValue] = useState(0);
  const [timeRange, setTimeRange] = useState('6m');
  const [market, setMarket] = useState('');
  const [trendData, setTrendData] = useState<any[]>([]);
  const [forecastData, setForecastData] = useState<any[]>([]);
  const [news, setNews] = useState<any[]>([]);

  useEffect(() => {
    loadMarketData();
  }, [timeRange, market]);

  const loadMarketData = async () => {
    try {
      setLoading(true);

      // Process trend data based on time range
      const months = timeRange === '3m' ? 3 : timeRange === '6m' ? 6 : 12;
      const mockTrendData = Array.from({ length: months }, (_, i) => ({
        month: new Date(Date.now() - (months - i - 1) * 30 * 24 * 60 * 60 * 1000).toLocaleString('default', { month: 'short' }),
        marketSize: 50 + Math.random() * 30,
        growthRate: 5 + Math.random() * 10,
        competitorShare: 20 + Math.random() * 15,
        yourShare: 10 + Math.random() * 20,
        sentiment: 0.5 + Math.random() * 0.5,
      }));
      setTrendData(mockTrendData);

      // Process forecast data
      const mockForecastData = Array.from({ length: 6 }, (_, i) => ({
        month: new Date(Date.now() + i * 30 * 24 * 60 * 60 * 1000).toLocaleString('default', { month: 'short' }),
        predicted: 60 + i * 5 + Math.random() * 10,
        confidence: 0.8 + Math.random() * 0.15,
        optimistic: 70 + i * 6,
        pessimistic: 50 + i * 3,
      }));
      setForecastData(mockForecastData);

      // Mock news data
      const mockNews = [
        {
          id: 1,
          title: 'AI Market Expected to Reach $190B by 2025',
          source: 'TechCrunch',
          date: '2025-01-14',
          sentiment: 'positive',
          impact: 'high',
          summary: 'The artificial intelligence market is projected to grow at a CAGR of 37% through 2025.',
        },
        {
          id: 2,
          title: 'Major Competitor Announces $500M Investment in R&D',
          source: 'Bloomberg',
          date: '2025-01-13',
          sentiment: 'negative',
          impact: 'high',
          summary: 'Competitor X announced significant investment in research and development, potentially threatening market position.',
        },
        {
          id: 3,
          title: 'New Regulations Could Impact Data Collection Practices',
          source: 'Reuters',
          date: '2025-01-12',
          sentiment: 'neutral',
          impact: 'medium',
          summary: 'Upcoming regulations may require changes to data collection and privacy policies.',
        },
      ];
      setNews(mockNews);

    } catch (err: any) {
      setError('Failed to load market data');
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
            Market Intelligence
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Real-time market trends, forecasts, and insights
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              label="Time Range"
              onChange={(e) => setTimeRange(e.target.value)}
            >
              <MenuItem value="3m">3 Months</MenuItem>
              <MenuItem value="6m">6 Months</MenuItem>
              <MenuItem value="12m">1 Year</MenuItem>
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Market</InputLabel>
            <Select
              value={market}
              label="Market"
              onChange={(e) => setMarket(e.target.value)}
            >
              <MenuItem value="">All Markets</MenuItem>
              <MenuItem value="ai">Artificial Intelligence</MenuItem>
              <MenuItem value="saas">SaaS</MenuItem>
              <MenuItem value="cloud">Cloud Computing</MenuItem>
            </Select>
          </FormControl>
          <Button variant="outlined" startIcon={<AutoGraphIcon />}>
            Generate Report
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Market Overview Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {[
          { title: 'Market Size', value: '$127.5B', change: '+12.3%', icon: <TrendingUpIcon />, color: '#2e7d32' },
          { title: 'Growth Rate', value: '37.5%', change: '+2.1%', icon: <AutoGraphIcon />, color: '#1976d2' },
          { title: 'Market Share', value: '18.2%', change: '+3.4%', icon: <TrendingUpIcon />, color: '#2e7d32' },
          { title: 'Competitor Share', value: '24.8%', change: '-1.2%', icon: <TrendingDownIcon />, color: '#c62828' },
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
          <Tab label="Trends" />
          <Tab label="Forecast" />
          <Tab label="News & Sentiment" />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Market Trends
                </Typography>
                <ResponsiveContainer width="100%" height={350}>
                  <AreaChart data={trendData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Area type="monotone" dataKey="marketSize" stroke="#1976d2" fill="#1976d2" fillOpacity={0.6} name="Market Size ($B)" />
                    <Area type="monotone" dataKey="yourShare" stroke="#2e7d32" fill="#2e7d32" fillOpacity={0.4} name="Your Share" />
                    <Area type="monotone" dataKey="competitorShare" stroke="#c62828" fill="#c62828" fillOpacity={0.4} name="Competitor Share" />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Key Metrics
                </Typography>
                {[
                  { label: 'Average Growth', value: '12.3%', trend: '+2.1%' },
                  { label: 'Market Volatility', value: 'Low', trend: 'Stable' },
                  { label: 'Sentiment Score', value: '0.72', trend: '+0.05' },
                  { label: 'Opportunity Index', value: '8.2/10', trend: '+0.8' },
                ].map((metric, index) => (
                  <Box key={index} sx={{ py: 1, borderBottom: index < 3 ? 1 : 0, borderColor: 'divider' }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2" color="text.secondary">
                        {metric.label}
                      </Typography>
                      <Typography variant="body2" color={metric.trend.startsWith('+') ? '#2e7d32' : '#c62828'}>
                        {metric.trend}
                      </Typography>
                    </Box>
                    <Typography variant="h6">
                      {metric.value}
                    </Typography>
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Market Forecast
                </Typography>
                <ResponsiveContainer width="100%" height={350}>
                  <LineChart data={forecastData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="predicted" stroke="#1976d2" strokeWidth={3} name="Predicted" />
                    <Line type="monotone" dataKey="optimistic" stroke="#2e7d32" strokeDasharray="5 5" name="Optimistic" />
                    <Line type="monotone" dataKey="pessimistic" stroke="#c62828" strokeDasharray="5 5" name="Pessimistic" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Forecast Summary
                </Typography>
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" paragraph>
                    Based on current market trends and historical data, we predict:
                  </Typography>
                  <Box sx={{ pl: 2 }}>
                    <Typography variant="body2" paragraph>
                      • Market growth of <strong>15-20%</strong> in next 6 months
                    </Typography>
                    <Typography variant="body2" paragraph>
                      • Increased competition in <strong>AI & ML</strong> segment
                    </Typography>
                    <Typography variant="body2" paragraph>
                      • Opportunities in <strong>enterprise solutions</strong>
                    </Typography>
                    <Typography variant="body2">
                      • Risk of <strong>price compression</strong> in Q3
                    </Typography>
                  </Box>
                  <Box sx={{ mt: 2, p: 2, backgroundColor: '#e3f2fd', borderRadius: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      Confidence Level
                    </Typography>
                    <Typography variant="h4" color="#1976d2">
                      82%
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Market News
                </Typography>
                <Box sx={{ mt: 2 }}>
                  {news.map((item) => (
                    <Card key={item.id} sx={{ mb: 2, cursor: 'pointer', '&:hover': { boxShadow: 3 } }}>
                      <CardContent>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                          <Box sx={{ flex: 1 }}>
                            <Typography variant="h6" gutterBottom>
                              {item.title}
                            </Typography>
                            <Typography variant="body2" color="text.secondary" paragraph>
                              {item.summary}
                            </Typography>
                            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                              <Typography variant="caption" color="text.secondary">
                                {item.source}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                •
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {item.date}
                              </Typography>
                            </Box>
                          </Box>
                          <Box sx={{ ml: 2 }}>
                            <Chip
                              label={item.sentiment}
                              color={item.sentiment === 'positive' ? 'success' : item.sentiment === 'negative' ? 'error' : 'default'}
                              size="small"
                            />
                          </Box>
                        </Box>
                      </CardContent>
                    </Card>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Sentiment Analysis
                </Typography>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={[
                    { name: 'Positive', value: 45, color: '#2e7d32' },
                    { name: 'Neutral', value: 35, color: '#757575' },
                    { name: 'Negative', value: 20, color: '#c62828' },
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" fill="#1976d2" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card sx={{ mt: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Impact Analysis
                </Typography>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={[
                    { name: 'High', value: 8, color: '#c62828' },
                    { name: 'Medium', value: 12, color: '#ed6c02' },
                    { name: 'Low', value: 5, color: '#2e7d32' },
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" fill="#1976d2" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>
    </Box>
  );
}