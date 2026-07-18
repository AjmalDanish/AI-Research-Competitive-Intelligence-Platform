import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Alert,
  CircularProgress,
  Paper,
  Divider,
  useMediaQuery,
  useTheme,
  Fab,
  Zoom,
  Chip,
} from '@mui/material';
import {
  Business as BusinessIcon,
  TrendingUp as TrendingUpIcon,
  Notifications as NotificationsIcon,
  Assessment as AssessmentIcon,
  Refresh as RefreshIcon,
  ArrowUpward,
  ArrowDownward,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
} from 'recharts';
import { competitorsAPI, marketAPI, alertsAPI } from '../services/api';

export default function Dashboard() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isTablet = useMediaQuery(theme.breakpoints.down('lg'));

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [competitors, setCompetitors] = useState<any[]>([]);
  const [trends, setTrends] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  const stats = [
    {
      title: 'Active Competitors',
      value: competitors.length,
      trend: '+12%',
      trendUp: true,
      icon: <BusinessIcon />,
      color: '#1976d2',
    },
    {
      title: 'Market Trends',
      value: trends.length,
      trend: '+8%',
      trendUp: true,
      icon: <TrendingUpIcon />,
      color: '#2e7d32',
    },
    {
      title: 'Active Alerts',
      value: alerts.filter((a: any) => !a.is_read).length,
      trend: '-5%',
      trendUp: false,
      icon: <NotificationsIcon />,
      color: '#ed6c02',
    },
    {
      title: 'Reports Generated',
      value: '24',
      trend: '+15%',
      trendUp: true,
      icon: <AssessmentIcon />,
      color: '#9c27b0',
    },
  ];

  const marketData = [
    { month: 'Jan', marketShare: 25, competitorShare: 30, otherShare: 45 },
    { month: 'Feb', marketShare: 27, competitorShare: 29, otherShare: 44 },
    { month: 'Mar', marketShare: 28, competitorShare: 28, otherShare: 44 },
    { month: 'Apr', marketShare: 30, competitorShare: 27, otherShare: 43 },
    { month: 'May', marketShare: 32, competitorShare: 26, otherShare: 42 },
    { month: 'Jun', marketShare: 35, competitorShare: 25, otherShare: 40 },
  ];

  const marketDistribution = [
    { name: 'Your Company', value: 35, color: '#1976d2' },
    { name: 'TechCorp', value: 25, color: '#dc004e' },
    { name: 'DataFlow', value: 20, color: '#ff9800' },
    { name: 'Others', value: 20, color: '#757575' },
  ];

  const competitorComparison = [
    { name: 'Your Company', score: 85 },
    { name: 'TechCorp', score: 78 },
    { name: 'DataFlow', score: 72 },
    { name: 'CloudNine', score: 68 },
  ];

  const recentMovements = [
    { type: 'competitor', title: 'TechCorp launched new AI platform', time: '2 hours ago', impact: 'high' },
    { type: 'market', title: 'Market share increased by 3%', time: '5 hours ago', impact: 'medium' },
    { type: 'alert', title: 'New competitor entering market', time: '1 day ago', impact: 'high' },
    { type: 'competitor', title: 'DataFlow acquired smaller startup', time: '2 days ago', impact: 'medium' },
  ];

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      // Load competitors
      let competitors = [];
      try {
        const competitorsResponse = await competitorsAPI.list();
        competitors = competitorsResponse.data?.competitors || competitorsResponse.data || [];
      } catch (e) {
        console.log('Using mock competitors data');
      }

      // Load market trends
      let trends = [];
      try {
        const marketResponse = await marketAPI.trends();
        trends = marketResponse.data?.trends || marketResponse.data || [];
      } catch (e) {
        console.log('Using mock trends data');
      }

      // Load alerts
      let alerts = [];
      try {
        const alertsResponse = await alertsAPI.list();
        alerts = alertsResponse.data?.alerts || alertsResponse.data || [];
      } catch (e) {
        console.log('Using mock alerts data');
      }

      // If no data, use mock data
      if (competitors.length === 0) {
        competitors = [
          { id: 1, name: 'TechCorp Industries', industry: 'Technology', status: 'active', website: 'https://techcorp.com' },
          { id: 2, name: 'DataFlow Systems', industry: 'Software', status: 'active', website: 'https://dataflow.com' },
          { id: 3, name: 'CloudNine Solutions', industry: 'Cloud Computing', status: 'active', website: 'https://cloudnine.com' },
        ];
      }

      if (trends.length === 0) {
        trends = [
          { id: 1, name: 'AI Platform Adoption', growth_rate: 35, market_size: 15000000000, direction: 'up' },
          { id: 2, name: 'Cloud Migration Acceleration', growth_rate: 45, market_size: 35000000000, direction: 'up' },
          { id: 3, name: 'Data Privacy Regulations', growth_rate: 25, market_size: 5000000000, direction: 'up' },
        ];
      }

      if (alerts.length === 0) {
        alerts = [
          { id: 1, title: 'Competitor Price Change', alert_type: 'pricing', severity: 'high', is_read: false },
          { id: 2, title: 'New Product Launch', alert_type: 'product', severity: 'medium', is_read: false },
          { id: 3, title: 'Market Trend Alert', alert_type: 'market', severity: 'medium', is_read: true },
        ];
      }

      setCompetitors(competitors);
      setTrends(trends);
      setAlerts(alerts);
      setLastUpdated(new Date());
    } catch (err: any) {
      setError('Failed to load dashboard data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
    // Auto-refresh every 5 minutes
    const interval = setInterval(loadDashboardData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', mt: 4 }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error}
      </Alert>
    );
  }

  const getMovementColor = (impact: string) => {
    switch (impact) {
      case 'high': return '#dc004e';
      case 'medium': return '#ed6c02';
      case 'low': return '#2e7d32';
      default: return '#757575';
    }
  };

  const getMovementIcon = (type: string) => {
    switch (type) {
      case 'competitor': return <BusinessIcon fontSize="small" />;
      case 'market': return <TrendingUpIcon fontSize="small" />;
      case 'alert': return <NotificationsIcon fontSize="small" />;
      default: return null;
    }
  };

  return (
    <Box sx={{ pb: isMobile ? 7 : 0 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
        <Box>
          <Typography variant={isMobile ? 'h5' : 'h4'} gutterBottom>
            Dashboard
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {lastUpdated.toLocaleTimeString()} - Competitive Intelligence Overview
          </Typography>
        </Box>
        <Chip
          label={`Updated ${Math.floor((Date.now() - lastUpdated.getTime()) / 60000)}m ago`}
          size="small"
          color="primary"
          variant="outlined"
        />
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={{ xs: 2, sm: 3 }} sx={{ mb: { xs: 2, sm: 3 } }}>
        {stats.map((stat) => (
          <Grid item xs={6} sm={6} md={3} key={stat.title}>
            <Card
              sx={{
                height: '100%',
                transition: 'transform 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 4,
                },
              }}
            >
              <CardContent sx={{ p: { xs: 1.5, sm: 2 } }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                  <Typography
                    color="text.secondary"
                    variant={isMobile ? 'caption' : 'body2'}
                    sx={{ fontWeight: 500 }}
                  >
                    {stat.title}
                  </Typography>
                  <Box sx={{ color: stat.color, fontSize: isMobile ? 20 : 24 }}>
                    {stat.icon}
                  </Box>
                </Box>
                <Typography
                  variant={isMobile ? 'h5' : 'h4'}
                  component="div"
                  sx={{ color: stat.color, fontWeight: 'bold' }}
                >
                  {stat.value}
                </Typography>
                {stat.trend && (
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                    {stat.trendUp ? (
                      <ArrowUpward sx={{ fontSize: 14, color: '#2e7d32', mr: 0.5 }} />
                    ) : (
                      <ArrowDownward sx={{ fontSize: 14, color: '#c62828', mr: 0.5 }} />
                    )}
                    <Typography variant="caption" color={stat.trendUp ? '#2e7d32' : '#c62828'}>
                      {stat.trend}
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Charts Section */}
      <Grid container spacing={{ xs: 2, sm: 3 }} sx={{ mb: { xs: 2, sm: 3 } }}>
        {/* Market Share Trend */}
        <Grid item xs={12} md={isMobile ? 12 : 8}>
          <Card>
            <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
              <Typography variant={isMobile ? 'subtitle1' : 'h6'} gutterBottom fontWeight="bold">
                Market Share Trends
              </Typography>
              <ResponsiveContainer width="100%" height={isMobile ? 200 : 300}>
                <LineChart data={marketData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" tick={{ fontSize: isMobile ? 10 : 12 }} />
                  <YAxis tick={{ fontSize: isMobile ? 10 : 12 }} />
                  <Tooltip />
                  <Line type="monotone" dataKey="marketShare" stroke="#1976d2" strokeWidth={isMobile ? 1 : 2} name="Your Share" />
                  <Line type="monotone" dataKey="competitorShare" stroke="#dc004e" strokeWidth={isMobile ? 1 : 2} name="Competitor Share" />
                  <Line type="monotone" dataKey="otherShare" stroke="#757575" strokeWidth={isMobile ? 1 : 2} name="Other" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Market Distribution */}
        <Grid item xs={12} md={isMobile ? 12 : 4}>
          <Card>
            <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
              <Typography variant={isMobile ? 'subtitle1' : 'h6'} gutterBottom fontWeight="bold">
                Market Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={isMobile ? 200 : 300}>
                <PieChart>
                  <Pie
                    data={marketDistribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={isMobile ? 40 : 60}
                    outerRadius={isMobile ? 60 : 80}
                    paddingAngle={5}
                    dataKey="value"
                    label={isMobile ? false : true}
                    labelLine={false}
                  >
                    {marketDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 1, justifyContent: 'center' }}>
                {marketDistribution.map((item) => (
                  <Chip
                    key={item.name}
                    label={`${item.name}: ${item.value}%`}
                    size="small"
                    sx={{
                      backgroundColor: item.color,
                      color: 'white',
                      fontSize: isMobile ? '0.7rem' : '0.8rem',
                    }}
                  />
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Competitor Comparison */}
      <Grid container spacing={{ xs: 2, sm: 3 }} sx={{ mb: { xs: 2, sm: 3 } }}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
              <Typography variant={isMobile ? 'subtitle1' : 'h6'} gutterBottom fontWeight="bold">
                Competitor Comparison
              </Typography>
              <ResponsiveContainer width="100%" height={isMobile ? 200 : 250}>
                <BarChart data={competitorComparison}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" tick={{ fontSize: isMobile ? 10 : 12 }} />
                  <YAxis tick={{ fontSize: isMobile ? 10 : 12 }} />
                  <Tooltip />
                  <Bar dataKey="score" fill="#1976d2" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Movements */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
              <Typography variant={isMobile ? 'subtitle1' : 'h6'} gutterBottom fontWeight="bold">
                Recent Movements
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {recentMovements.slice(0, 4).map((movement, index) => (
                  <Box key={index}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                      <Box sx={{ color: getMovementColor(movement.impact) }}>
                        {getMovementIcon(movement.type)}
                      </Box>
                      <Typography variant={isMobile ? 'caption' : 'body2'} fontWeight="500">
                        {movement.title}
                      </Typography>
                    </Box>
                    <Typography variant="caption" color="text.secondary" sx={{ ml: 3 }}>
                      {movement.time}
                    </Typography>
                    {index < recentMovements.length - 1 && <Divider sx={{ mt: 1 }} />}
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Key Insights */}
      <Card sx={{ mt: { xs: 2, sm: 3 } }}>
        <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
          <Typography variant={isMobile ? 'subtitle1' : 'h6'} gutterBottom fontWeight="bold">
            Key Insights & Opportunities
          </Typography>
          <Grid container spacing={{ xs: 1, sm: 2 }}>
            {[
              {
                title: 'Growing Market Share',
                description: 'Your market share has increased by 10% over the last 6 months.',
                color: '#2e7d32',
              },
              {
                title: 'Competitor Innovation',
                description: 'TechCorp is investing heavily in AI capabilities - monitor closely.',
                color: '#ed6c02',
              },
              {
                title: 'New Opportunities',
                description: 'Enterprise segment showing strong growth potential.',
                color: '#1976d2',
              },
            ].map((insight, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Paper
                  elevation={2}
                  sx={{
                    p: { xs: 1.5, sm: 2 },
                    borderLeft: 4,
                    borderColor: insight.color,
                    height: '100%',
                  }}
                >
                  <Typography variant={isMobile ? 'subtitle2' : 'subtitle1'} fontWeight="bold" sx={{ color: insight.color }}>
                    {insight.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    {insight.description}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      {/* Floating Refresh Button */}
      <Zoom in={!loading}>
        <Fab
          color="primary"
          aria-label="refresh"
          onClick={loadDashboardData}
          sx={{
            position: 'fixed',
            bottom: { xs: 80, md: 24 },
            right: 24,
            zIndex: 1000,
          }}
          size="small"
        >
          <RefreshIcon />
        </Fab>
      </Zoom>
    </Box>
  );
}