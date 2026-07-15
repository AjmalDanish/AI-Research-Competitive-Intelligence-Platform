import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Chip,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  MenuItem,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Business as BusinessIcon,
  Visibility as VisibilityIcon,
} from '@mui/icons-material';
import { competitorsAPI } from '../services/api';

interface Competitor {
  id: string;
  name: string;
  website: string;
  industry: string;
  description?: string;
  founded_year?: number;
  headquarters?: string;
  market_cap?: number;
  employees?: number;
  status: string;
}

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

export default function Competitors() {
  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [tabValue, setTabValue] = useState(0);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingCompetitor, setEditingCompetitor] = useState<Competitor | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    website: '',
    industry: '',
    description: '',
    founded_year: '',
    headquarters: '',
    market_cap: '',
    employees: '',
    status: 'active',
  });

  useEffect(() => {
    loadCompetitors();
  }, []);

  const loadCompetitors = async () => {
    try {
      setLoading(true);
      const response = await competitorsAPI.list();
      setCompetitors(response.data || []);
    } catch (err: any) {
      setError('Failed to load competitors');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (competitor?: Competitor) => {
    if (competitor) {
      setEditingCompetitor(competitor);
      setFormData({
        name: competitor.name,
        website: competitor.website,
        industry: competitor.industry,
        description: competitor.description || '',
        founded_year: competitor.founded_year?.toString() || '',
        headquarters: competitor.headquarters || '',
        market_cap: competitor.market_cap?.toString() || '',
        employees: competitor.employees?.toString() || '',
        status: competitor.status,
      });
    } else {
      setEditingCompetitor(null);
      setFormData({
        name: '',
        website: '',
        industry: '',
        description: '',
        founded_year: '',
        headquarters: '',
        market_cap: '',
        employees: '',
        status: 'active',
      });
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingCompetitor(null);
    setFormData({
      name: '',
      website: '',
      industry: '',
      description: '',
      founded_year: '',
      headquarters: '',
      market_cap: '',
      employees: '',
      status: 'active',
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const data = {
        ...formData,
        founded_year: formData.founded_year ? parseInt(formData.founded_year) : undefined,
        market_cap: formData.market_cap ? parseFloat(formData.market_cap) : undefined,
        employees: formData.employees ? parseInt(formData.employees) : undefined,
      };

      if (editingCompetitor) {
        await competitorsAPI.update(editingCompetitor.id, data);
      } else {
        await competitorsAPI.create(data);
      }

      handleCloseDialog();
      loadCompetitors();
    } catch (err: any) {
      setError(editingCompetitor ? 'Failed to update competitor' : 'Failed to create competitor');
      console.error(err);
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this competitor?')) {
      try {
        await competitorsAPI.delete(id);
        loadCompetitors();
      } catch (err: any) {
        setError('Failed to delete competitor');
        console.error(err);
      }
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
            Competitors
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Monitor and analyze your competition
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Competitor
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
          <Tab label="Grid View" />
          <Tab label="Table View" />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          {competitors.map((competitor) => (
            <Grid item xs={12} sm={6} md={4} key={competitor.id}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <BusinessIcon sx={{ fontSize: 40, color: '#1976d2' }} />
                      <Box>
                        <Typography variant="h6">{competitor.name}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {competitor.industry}
                        </Typography>
                      </Box>
                    </Box>
                    <Chip
                      label={competitor.status}
                      color={competitor.status === 'active' ? 'success' : 'default'}
                      size="small"
                    />
                  </Box>

                  <Box sx={{ mt: 2 }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {competitor.description}
                    </Typography>
                  </Box>

                  <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {competitor.headquarters && (
                      <Chip label={`📍 ${competitor.headquarters}`} size="small" variant="outlined" />
                    )}
                    {competitor.employees && (
                      <Chip label={`👥 ${competitor.employees.toLocaleString()} employees`} size="small" variant="outlined" />
                    )}
                    {competitor.founded_year && (
                      <Chip label={`📅 Since ${competitor.founded_year}`} size="small" variant="outlined" />
                    )}
                  </Box>

                  <Box sx={{ mt: 2, display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                    <IconButton size="small" onClick={() => handleOpenDialog(competitor)}>
                      <EditIcon />
                    </IconButton>
                    <IconButton size="small" color="error" onClick={() => handleDelete(competitor.id)}>
                      <DeleteIcon />
                    </IconButton>
                    <IconButton size="small">
                      <VisibilityIcon />
                    </IconButton>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Company</TableCell>
                <TableCell>Industry</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Employees</TableCell>
                <TableCell>Market Cap</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {competitors.map((competitor) => (
                <TableRow key={competitor.id} hover>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <BusinessIcon sx={{ color: '#1976d2' }} />
                      <Box>
                        <Typography variant="body2" fontWeight="medium">
                          {competitor.name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {competitor.website}
                        </Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell>{competitor.industry}</TableCell>
                  <TableCell>
                    <Chip
                      label={competitor.status}
                      color={competitor.status === 'active' ? 'success' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {competitor.employees ? competitor.employees.toLocaleString() : 'N/A'}
                  </TableCell>
                  <TableCell>
                    {competitor.market_cap
                      ? `$${(competitor.market_cap / 1e9).toFixed(1)}B`
                      : 'N/A'}
                  </TableCell>
                  <TableCell>
                    <IconButton size="small" onClick={() => handleOpenDialog(competitor)}>
                      <EditIcon />
                    </IconButton>
                    <IconButton size="small" color="error" onClick={() => handleDelete(competitor.id)}>
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>

      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingCompetitor ? 'Edit Competitor' : 'Add New Competitor'}
        </DialogTitle>
        <form onSubmit={handleSubmit}>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              label="Company Name"
              fullWidth
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
            <TextField
              margin="dense"
              label="Website"
              fullWidth
              value={formData.website}
              onChange={(e) => setFormData({ ...formData, website: e.target.value })}
              required
            />
            <TextField
              margin="dense"
              label="Industry"
              fullWidth
              value={formData.industry}
              onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
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
            <TextField
              margin="dense"
              label="Founded Year"
              type="number"
              fullWidth
              value={formData.founded_year}
              onChange={(e) => setFormData({ ...formData, founded_year: e.target.value })}
            />
            <TextField
              margin="dense"
              label="Headquarters"
              fullWidth
              value={formData.headquarters}
              onChange={(e) => setFormData({ ...formData, headquarters: e.target.value })}
            />
            <TextField
              margin="dense"
              label="Market Cap (USD)"
              type="number"
              fullWidth
              value={formData.market_cap}
              onChange={(e) => setFormData({ ...formData, market_cap: e.target.value })}
            />
            <TextField
              margin="dense"
              label="Number of Employees"
              type="number"
              fullWidth
              value={formData.employees}
              onChange={(e) => setFormData({ ...formData, employees: e.target.value })}
            />
            <TextField
              margin="dense"
              label="Status"
              select
              fullWidth
              value={formData.status}
              onChange={(e) => setFormData({ ...formData, status: e.target.value })}
            >
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="inactive">Inactive</MenuItem>
              <MenuItem value="acquired">Acquired</MenuItem>
            </TextField>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Cancel</Button>
            <Button type="submit" variant="contained">
              {editingCompetitor ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
}