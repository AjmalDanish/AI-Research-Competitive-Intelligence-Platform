import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Business as BusinessIcon,
  TrendingUp as TrendingUpIcon,
  Notifications as NotificationsIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { competitorsAPI, marketAPI, alertsAPI } from '../services/api';

interface StatCard {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color: string;
  trend?: string;
}

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [stats, setStats] = useState<StatCard[]>([]);
  const [marketData, setMarketData] = useState<any[]>([]);
  const [competitorData, setCompetitorData] = useState<any[]>([]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      // Load competitors
      const competitorsResponse = await competitorsAPI.list();
      const competitors = competitorsResponse.data || [];

      // Load market trends
      const marketResponse = await marketAPI.trends();
      const trends = marketResponse.data || [];

      // Load alerts
      const alertsResponse = await alertsAPI.list();
      const alerts = alertsResponse.data || [];

      // Create stats cards
      const newStats: StatCard[] = [
        {
          title: 'Active Competitors',
          value: competitors.length,
          icon: <BusinessIcon fontSize="large" />,
          color: '#1976d2',
          trend: '+3 this month',
        },
        {
          title: 'Market Trends',
          value: trends.length,
          icon: <TrendingUpIcon fontSize="large" />,
          color: '#2e7d32',
          trend: '+12% growth',
        },
        {
          title: 'Active Alerts',
          value: alerts.filter((a: any) => !a.is_read).length,
          icon: <NotificationsIcon fontSize="large" />,
          color: '#ed6c02',
          trend: '5 new today',
        },
        {
          title: 'Reports Generated',
          value: '24',
          icon: <AssessmentIcon fontSize="large" />,
          color: '#9c27b0',
          trend: '+8 this week',
        },
      ];

      setStats(newStats);

      // Create mock market data
      const mockMarketData = [
        { month: 'Jan', marketShare: 30, competitorShare: 25, otherShare: 45 },
        { month: 'Feb', marketShare: 32, competitorShare: 27, otherShare: 41 },
        { month: 'Mar', marketShare: 35, competitorShare: 28, otherShare: 37 },
        { month: 'Apr', marketShare: 33, competitorShare: 30, otherShare: 37 },
        { month: 'May', marketShare: 38, competitorShare: 29, otherShare: 33 },
        { month: 'Jun', marketShare: 40, competitorShare: 28, otherShare: 32 },
      ];
      setMarketData(mockMarketData);

      // Create mock competitor data
      const mockCompetitorData = [
        { name: 'Your Company', value: 40, color: '#1976d2' },
        { name: 'Competitor A', value: 28, color: '#dc004e' },
        { name: 'Competitor B', value: 18, color: '#ed6c02' },
        { name: 'Others', value: 14, color: '#757575' },
      ];
      setCompetitorData(mockCompetitorData);

    } catch (err: any) {
      setError('Failed to load dashboard data');
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

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" gutterBottom>
        Overview of your competitive intelligence
      </Typography>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mt: 1 }}>
        {stats.map((stat) => (
          <Grid item xs={12} sm={6} md={3} key={stat.title}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box>
                    <Typography color="text.secondary" variant="body2" gutterBottom>
                      {stat.title}
                    </Typography>
                    <Typography variant="h4" component="div" sx={{ color: stat.color }}>
                      {stat.value}
                    </Typography>
                    {stat.trend && (
                      <Typography variant="caption" color="text.secondary">
                        {stat.trend}
                      </Typography>
                    )}
                  </Box>
                  <Box sx={{ color: stat.color }}>
                    {stat.icon}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mt: 3 }}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Market Share Trends
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={marketData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="marketShare" stroke="#1976d2" strokeWidth={2} name="Your Share" />
                  <Line type="monotone" dataKey="competitorShare" stroke="#dc004e" strokeWidth={2} name="Competitor Share" />
                  <Line type="monotone" dataKey="otherShare" stroke="#757575" strokeWidth={2} name="Other" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Market Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={competitorData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {competitorData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Activity */}
      <Grid container spacing={3} sx={{ mt: 3 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Market Movements
              </Typography>
              <Box sx={{ mt: 2 }}>
                {[
                  { company: 'Competitor A', action: 'launched new product', time: '2 hours ago', impact: 'high' },
                  { company: 'Competitor B', action: 'announced partnership', time: '5 hours ago', impact: 'medium' },
                  { company: 'Competitor C', action: 'lowered prices', time: '1 day ago', impact: 'high' },
                  { company: 'Competitor A', action: 'hired new CEO', time: '2 days ago', impact: 'medium' },
                ].map((item, index) => (
                  <Box key={index} sx={{ py: 1, borderBottom: index < 3 ? 1 : 0, borderColor: 'divider' }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2" fontWeight="medium">
                        {item.company}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {item.time}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {item.action}
                    </Typography>
                    <Box sx={{ mt: 0.5 }}>
                      <Typography
                        variant="caption"
                        sx={{
                          px: 1,
                          py: 0.25,
                          borderRadius: 1,
                          backgroundColor:
                            item.impact === 'high' ? '#ffebee' : item.impact === 'medium' ? '#fff3e0' : '#e8f5e9',
                          color:
                            item.impact === 'high' ? '#c62828' : item.impact === 'medium' ? '#e65100' : '#2e7d32',
                        }}
                      >
                        {item.impact.toUpperCase()} IMPACT
                      </Typography>
                    </Box>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Key Insights
              </Typography>
              <Box sx={{ mt: 2 }}>
                {[
                  { type: 'opportunity', text: 'Market gap in premium segment identified', priority: 'high' },
                  { type: 'risk', text: 'Competitor A gaining market share rapidly', priority: 'high' },
                  { type: 'opportunity', text: 'New technology trends favor your product line', priority: 'medium' },
                  { type: 'risk', text: 'Price war expected in Q3', priority: 'medium' },
                ].map((item, index) => (
                  <Box key={index} sx={{ py: 1, borderBottom: index < 3 ? 1 : 0, borderColor: 'divider' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box
                        sx={{
                          width: 8,
                          height: 8,
                          borderRadius: '50%',
                          backgroundColor: item.type === 'opportunity' ? '#2e7d32' : '#c62828',
                        }}
                      />
                      <Typography variant="body2">
                        {item.text}
                      </Typography>
                    </Box>
                    <Typography variant="caption" color="text.secondary" sx={{ ml: 2 }}>
                      {item.priority.toUpperCase()} PRIORITY
                    </Typography>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}