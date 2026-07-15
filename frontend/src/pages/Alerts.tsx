import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Chip,
  Switch,
  FormControlLabel,
  CircularProgress,
  Alert,
  Grid,
  IconButton,
  Badge,
} from '@mui/material';
import {
  Add as AddIcon,
  NotificationsActive as NotificationsActiveIcon,
  CheckCircle as CheckCircleIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  MarkEmailRead as MarkEmailReadIcon,
  FilterList as FilterListIcon,
} from '@mui/icons-material';
import { alertsAPI } from '../services/api';

interface Alert {
  id: string;
  title: string;
  description: string;
  type: 'competitor' | 'market' | 'pricing' | 'product' | 'news';
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'active' | 'triggered' | 'resolved';
  is_read: boolean;
  created_at: string;
  triggered_at?: string;
}

export default function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('all');
  const [showUnreadOnly, setShowUnreadOnly] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingAlert, setEditingAlert] = useState<Alert | null>(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    type: 'competitor',
    severity: 'medium',
  });

  useEffect(() => {
    loadAlerts();
  }, [filter, showUnreadOnly]);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      const response = await alertsAPI.list();
      let filteredAlerts = response.data || [];

      if (filter !== 'all') {
        filteredAlerts = filteredAlerts.filter((alert: Alert) => alert.type === filter);
      }

      if (showUnreadOnly) {
        filteredAlerts = filteredAlerts.filter((alert: Alert) => !alert.is_read);
      }

      setAlerts(filteredAlerts);
    } catch (err: any) {
      setError('Failed to load alerts');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (alert?: Alert) => {
    if (alert) {
      setEditingAlert(alert);
      setFormData({
        title: alert.title,
        description: alert.description,
        type: alert.type,
        severity: alert.severity,
      });
    } else {
      setEditingAlert(null);
      setFormData({
        title: '',
        description: '',
        type: 'competitor',
        severity: 'medium',
      });
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingAlert(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingAlert) {
        await alertsAPI.update(editingAlert.id, formData);
      } else {
        await alertsAPI.create(formData);
      }
      handleCloseDialog();
      loadAlerts();
    } catch (err: any) {
      setError(editingAlert ? 'Failed to update alert' : 'Failed to create alert');
      console.error(err);
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this alert?')) {
      try {
        await alertsAPI.delete(id);
        loadAlerts();
      } catch (err: any) {
        setError('Failed to delete alert');
        console.error(err);
      }
    }
  };

  const handleMarkAsRead = async (id: string) => {
    try {
      await alertsAPI.markRead(id);
      loadAlerts();
    } catch (err: any) {
      setError('Failed to mark alert as read');
      console.error(err);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return '#c62828';
      case 'high': return '#d32f2f';
      case 'medium': return '#ed6c02';
      case 'low': return '#2e7d32';
      default: return '#757575';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return '#1976d2';
      case 'triggered': return '#ed6c02';
      case 'resolved': return '#2e7d32';
      default: return '#757575';
    }
  };

  const unreadCount = alerts.filter(a => !a.is_read).length;

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
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Box>
            <Typography variant="h4" gutterBottom>
              Alerts & Notifications
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              Stay informed about important events
            </Typography>
          </Box>
          {unreadCount > 0 && (
            <Badge badgeContent={unreadCount} color="error">
              <NotificationsActiveIcon />
            </Badge>
          )}
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Create Alert
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6} md={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Filter by Type</InputLabel>
                <Select
                  value={filter}
                  label="Filter by Type"
                  onChange={(e) => setFilter(e.target.value)}
                  startIcon={<FilterListIcon />}
                >
                  <MenuItem value="all">All Types</MenuItem>
                  <MenuItem value="competitor">Competitor</MenuItem>
                  <MenuItem value="market">Market</MenuItem>
                  <MenuItem value="pricing">Pricing</MenuItem>
                  <MenuItem value="product">Product</MenuItem>
                  <MenuItem value="news">News</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <FormControlLabel
                control={
                  <Switch
                    checked={showUnreadOnly}
                    onChange={(e) => setShowUnreadOnly(e.target.checked)}
                  />
                }
                label="Show Unread Only"
              />
            </Grid>
            <Grid item xs={12} sm={12} md={4}>
              <Typography variant="body2" color="text.secondary">
                Showing {alerts.length} {alerts.length === 1 ? 'alert' : 'alerts'}
                {unreadCount > 0 && ` (${unreadCount} unread)`}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Alerts List */}
      <Grid container spacing={2}>
        {alerts.length === 0 ? (
          <Grid item xs={12}>
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 8 }}>
                <NotificationsActiveIcon sx={{ fontSize: 64, color: '#bdbdbd', mb: 2 }} />
                <Typography variant="h6" color="text.secondary">
                  No alerts found
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Create an alert to start monitoring
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ) : (
          alerts.map((alert) => (
            <Grid item xs={12} key={alert.id}>
              <Card
                sx={{
                  borderLeft: 4,
                  borderColor: getSeverityColor(alert.severity),
                  backgroundColor: alert.is_read ? 'inherit' : '#f5f5f5',
                }}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Box sx={{ flex: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <Typography variant="h6" component="div">
                          {alert.title}
                        </Typography>
                        {!alert.is_read && (
                          <Chip label="New" color="primary" size="small" />
                        )}
                        <Chip
                          label={alert.type}
                          size="small"
                          variant="outlined"
                        />
                        <Chip
                          label={alert.severity}
                          size="small"
                          sx={{
                            backgroundColor: getSeverityColor(alert.severity),
                            color: 'white',
                          }}
                        />
                        <Chip
                          label={alert.status}
                          size="small"
                          sx={{
                            backgroundColor: getStatusColor(alert.status),
                            color: 'white',
                          }}
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary" paragraph>
                        {alert.description}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                        <Typography variant="caption" color="text.secondary">
                          Created: {new Date(alert.created_at).toLocaleString()}
                        </Typography>
                        {alert.triggered_at && (
                          <Typography variant="caption" color="text.secondary">
                            Triggered: {new Date(alert.triggered_at).toLocaleString()}
                          </Typography>
                        )}
                      </Box>
                    </Box>
                    <Box sx={{ display: 'flex', gap: 1, ml: 2 }}>
                      {!alert.is_read && (
                        <IconButton
                          size="small"
                          onClick={() => handleMarkAsRead(alert.id)}
                          title="Mark as read"
                        >
                          <MarkEmailReadIcon />
                        </IconButton>
                      )}
                      <IconButton
                        size="small"
                        onClick={() => handleOpenDialog(alert)}
                        title="Edit"
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleDelete(alert.id)}
                        title="Delete"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))
        )}
      </Grid>

      {/* Create/Edit Alert Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingAlert ? 'Edit Alert' : 'Create New Alert'}
        </DialogTitle>
        <form onSubmit={handleSubmit}>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              label="Alert Title"
              fullWidth
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              required
            />
            <TextField
              margin="dense"
              label="Description"
              fullWidth
              multiline
              rows={4}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              required
            />
            <FormControl fullWidth margin="dense">
              <InputLabel>Alert Type</InputLabel>
              <Select
                value={formData.type}
                label="Alert Type"
                onChange={(e) => setFormData({ ...formData, type: e.target.value as any })}
              >
                <MenuItem value="competitor">Competitor Activity</MenuItem>
                <MenuItem value="market">Market Change</MenuItem>
                <MenuItem value="pricing">Price Change</MenuItem>
                <MenuItem value="product">Product Launch</MenuItem>
                <MenuItem value="news">News & Updates</MenuItem>
              </Select>
            </FormControl>
            <FormControl fullWidth margin="dense">
              <InputLabel>Severity</InputLabel>
              <Select
                value={formData.severity}
                label="Severity"
                onChange={(e) => setFormData({ ...formData, severity: e.target.value as any })}
              >
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="critical">Critical</MenuItem>
              </Select>
            </FormControl>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Cancel</Button>
            <Button type="submit" variant="contained">
              {editingAlert ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
}