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
  Grid,
  Chip,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
} from '@mui/material';
import {
  Add as AddIcon,
  Download as DownloadIcon,
  Description as DescriptionIcon,
  PictureAsPdf as PictureAsPdfIcon,
  TableChart as TableChartIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
} from '@mui/icons-material';
import { reportsAPI } from '../services/api';

interface Report {
  id: string;
  title: string;
  description: string;
  type: 'competitor' | 'market' | 'analytics' | 'custom';
  format: 'pdf' | 'excel' | 'csv';
  status: 'generating' | 'ready' | 'failed';
  created_at: string;
  file_size?: string;
}

export default function Reports() {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    type: 'competitor',
    format: 'pdf',
    date_range: '30d',
  });

  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    try {
      setLoading(true);
      const response = await reportsAPI.list();
      setReports(response.data || []);
    } catch (err: any) {
      setError('Failed to load reports');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateReport = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setGenerating(true);
      await reportsAPI.generate(formData);
      handleCloseDialog();
      loadReports();
    } catch (err: any) {
      setError('Failed to generate report');
      console.error(err);
    } finally {
      setGenerating(false);
    }
  };

  const handleDownload = async (id: string) => {
    try {
      const response = await reportsAPI.download(id);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `report-${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err: any) {
      setError('Failed to download report');
      console.error(err);
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this report?')) {
      try {
        // await reportsAPI.delete(id);
        setReports(reports.filter(r => r.id !== id));
      } catch (err: any) {
        setError('Failed to delete report');
        console.error(err);
      }
    }
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setFormData({
      title: '',
      description: '',
      type: 'competitor',
      format: 'pdf',
      date_range: '30d',
    });
  };

  const getFormatIcon = (format: string) => {
    switch (format) {
      case 'pdf': return <PictureAsPdfIcon sx={{ color: '#c62828' }} />;
      case 'excel': return <TableChartIcon sx={{ color: '#2e7d32' }} />;
      case 'csv': return <DescriptionIcon sx={{ color: '#1976d2' }} />;
      default: return <DescriptionIcon />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ready': return '#2e7d32';
      case 'generating': return '#ed6c02';
      case 'failed': return '#c62828';
      default: return '#757575';
    }
  };

  const reportTemplates = [
    {
      title: 'Competitor Analysis Report',
      description: 'Comprehensive analysis of all tracked competitors including market position, strengths, and weaknesses.',
      type: 'competitor',
    },
    {
      title: 'Market Intelligence Report',
      description: 'Market trends, forecasts, and opportunities analysis with actionable insights.',
      type: 'market',
    },
    {
      title: 'Performance Analytics Report',
      description: 'Detailed performance metrics, competitive positioning, and growth analysis.',
      type: 'analytics',
    },
    {
      title: 'SWOT Analysis Report',
      description: 'Strategic SWOT analysis with recommendations and risk assessment.',
      type: 'analytics',
    },
  ];

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
            Reports
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Generate and download analytical reports
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setDialogOpen(true)}
        >
          Generate Report
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {/* Report Templates */}
      <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
        Quick Report Templates
      </Typography>
      <Grid container spacing={2} sx={{ mb: 4 }}>
        {reportTemplates.map((template, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card
              sx={{
                height: '100%',
                cursor: 'pointer',
                transition: 'transform 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 4,
                },
              }}
              onClick={() => {
                setFormData({
                  ...formData,
                  title: template.title,
                  description: template.description,
                  type: template.type,
                });
                setDialogOpen(true);
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <DescriptionIcon sx={{ color: '#1976d2', fontSize: 32 }} />
                  <Typography variant="subtitle1" fontWeight="medium">
                    {template.title}
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  {template.description}
                </Typography>
                <Box sx={{ mt: 2 }}>
                  <Chip label={template.type} size="small" variant="outlined" />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Recent Reports */}
      <Typography variant="h6" gutterBottom>
        Recent Reports
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Report</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Format</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Size</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {reports.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  <Box sx={{ py: 4 }}>
                    <DescriptionIcon sx={{ fontSize: 48, color: '#bdbdbd', mb: 1 }} />
                    <Typography variant="body1" color="text.secondary">
                      No reports generated yet
                    </Typography>
                  </Box>
                </TableCell>
              </TableRow>
            ) : (
              reports.map((report) => (
                <TableRow key={report.id} hover>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {getFormatIcon(report.format)}
                      <Box>
                        <Typography variant="body2" fontWeight="medium">
                          {report.title}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {report.description}
                        </Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip label={report.type} size="small" variant="outlined" />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={report.format.toUpperCase()}
                      size="small"
                      icon={getFormatIcon(report.format)}
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={report.status}
                      size="small"
                      sx={{
                        backgroundColor: getStatusColor(report.status),
                        color: 'white',
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    {report.file_size || '-'}
                  </TableCell>
                  <TableCell>
                    {new Date(report.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                      <IconButton
                        size="small"
                        onClick={() => handleDownload(report.id)}
                        disabled={report.status !== 'ready'}
                        title="Download"
                      >
                        <DownloadIcon />
                      </IconButton>
                      <IconButton size="small" title="View">
                        <VisibilityIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleDelete(report.id)}
                        title="Delete"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Box>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Generate Report Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          Generate Report
        </DialogTitle>
        <form onSubmit={handleGenerateReport}>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              label="Report Title"
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
              rows={3}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            />
            <FormControl fullWidth margin="dense">
              <InputLabel>Report Type</InputLabel>
              <Select
                value={formData.type}
                label="Report Type"
                onChange={(e) => setFormData({ ...formData, type: e.target.value as any })}
              >
                <MenuItem value="competitor">Competitor Analysis</MenuItem>
                <MenuItem value="market">Market Intelligence</MenuItem>
                <MenuItem value="analytics">Performance Analytics</MenuItem>
                <MenuItem value="custom">Custom Report</MenuItem>
              </Select>
            </FormControl>
            <FormControl fullWidth margin="dense">
              <InputLabel>Format</InputLabel>
              <Select
                value={formData.format}
                label="Format"
                onChange={(e) => setFormData({ ...formData, format: e.target.value as any })}
              >
                <MenuItem value="pdf">PDF</MenuItem>
                <MenuItem value="excel">Excel</MenuItem>
                <MenuItem value="csv">CSV</MenuItem>
              </Select>
            </FormControl>
            <FormControl fullWidth margin="dense">
              <InputLabel>Date Range</InputLabel>
              <Select
                value={formData.date_range}
                label="Date Range"
                onChange={(e) => setFormData({ ...formData, date_range: e.target.value })}
              >
                <MenuItem value="7d">Last 7 days</MenuItem>
                <MenuItem value="30d">Last 30 days</MenuItem>
                <MenuItem value="90d">Last 90 days</MenuItem>
                <MenuItem value="365d">Last year</MenuItem>
                <MenuItem value="custom">Custom range</MenuItem>
              </Select>
            </FormControl>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog} disabled={generating}>
              Cancel
            </Button>
            <Button type="submit" variant="contained" disabled={generating}>
              {generating ? <CircularProgress size={20} /> : 'Generate'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
}