import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  TextField,
  Switch,
  FormControlLabel,
  Divider,
  Grid,
  Alert,
  Tabs,
  Tab,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import {
  Person as PersonIcon,
  Notifications as NotificationsIcon,
  Security as SecurityIcon,
  Storage as StorageIcon,
  Palette as PaletteIcon,
  Save as SaveIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

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

export default function Settings() {
  const { user } = useAuth();
  const [tabValue, setTabValue] = useState(0);
  const [saved, setSaved] = useState(false);
  const [profileData, setProfileData] = useState({
    full_name: user?.full_name || '',
    email: user?.email || '',
    username: user?.username || '',
    phone: '',
    company: '',
    title: '',
  });
  const [notificationSettings, setNotificationSettings] = useState({
    email_alerts: true,
    push_notifications: true,
    weekly_digest: false,
    competitor_updates: true,
    market_changes: true,
    price_alerts: false,
  });
  const [apiSettings, setApiSettings] = useState({
    api_key: '',
    webhook_url: '',
    rate_limit: '1000',
    cache_duration: '3600',
  });
  const [displaySettings, setDisplaySettings] = useState({
    theme: 'light',
    language: 'en',
    timezone: 'UTC',
    date_format: 'YYYY-MM-DD',
    currency: 'USD',
  });

  const handleSaveProfile = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const handleSaveNotifications = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const handleSaveAPI = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const handleSaveDisplay = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Settings
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Manage your account and preferences
        </Typography>
      </Box>

      {saved && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Settings saved successfully
        </Alert>
      )}

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
          <Tab icon={<PersonIcon />} label="Profile" />
          <Tab icon={<NotificationsIcon />} label="Notifications" />
          <Tab icon={<SecurityIcon />} label="API & Security" />
          <Tab icon={<PaletteIcon />} label="Display" />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Profile Information
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Full Name"
                      value={profileData.full_name}
                      onChange={(e) => setProfileData({ ...profileData, full_name: e.target.value })}
                      margin="normal"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Username"
                      value={profileData.username}
                      onChange={(e) => setProfileData({ ...profileData, username: e.target.value })}
                      margin="normal"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Email"
                      type="email"
                      value={profileData.email}
                      onChange={(e) => setProfileData({ ...profileData, email: e.target.value })}
                      margin="normal"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Phone"
                      value={profileData.phone}
                      onChange={(e) => setProfileData({ ...profileData, phone: e.target.value })}
                      margin="normal"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Company"
                      value={profileData.company}
                      onChange={(e) => setProfileData({ ...profileData, company: e.target.value })}
                      margin="normal"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Job Title"
                      value={profileData.title}
                      onChange={(e) => setProfileData({ ...profileData, title: e.target.value })}
                      margin="normal"
                    />
                  </Grid>
                </Grid>
                <Button
                  variant="contained"
                  startIcon={<SaveIcon />}
                  onClick={handleSaveProfile}
                  sx={{ mt: 2 }}
                >
                  Save Profile
                </Button>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Change Password
                </Typography>
                <TextField
                  fullWidth
                  label="Current Password"
                  type="password"
                  margin="normal"
                />
                <TextField
                  fullWidth
                  label="New Password"
                  type="password"
                  margin="normal"
                />
                <TextField
                  fullWidth
                  label="Confirm Password"
                  type="password"
                  margin="normal"
                />
                <Button
                  variant="outlined"
                  sx={{ mt: 2 }}
                >
                  Update Password
                </Button>
              </CardContent>
            </Card>

            <Card sx={{ mt: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Account Statistics
                </Typography>
                <Box sx={{ mt: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      Competitors Tracked
                    </Typography>
                    <Typography variant="body2" fontWeight="medium">
                      12
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      Reports Generated
                    </Typography>
                    <Typography variant="body2" fontWeight="medium">
                      24
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      Alerts Created
                    </Typography>
                    <Typography variant="body2" fontWeight="medium">
                      8
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">
                      Member Since
                    </Typography>
                    <Typography variant="body2" fontWeight="medium">
                      Jan 2025
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Email Notifications
                </Typography>
                <Divider sx={{ my: 2 }} />
                {[
                  { key: 'email_alerts', label: 'Email Alerts' },
                  { key: 'weekly_digest', label: 'Weekly Digest' },
                  { key: 'competitor_updates', label: 'Competitor Updates' },
                  { key: 'market_changes', label: 'Market Changes' },
                  { key: 'price_alerts', label: 'Price Alerts' },
                ].map((item) => (
                  <FormControlLabel
                    key={item.key}
                    control={
                      <Switch
                        checked={notificationSettings[item.key as keyof typeof notificationSettings]}
                        onChange={(e) =>
                          setNotificationSettings({
                            ...notificationSettings,
                            [item.key]: e.target.checked,
                          })
                        }
                      />
                    }
                    label={item.label}
                    sx={{ display: 'flex', width: '100%', mb: 1 }}
                  />
                ))}
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Push Notifications
                </Typography>
                <Divider sx={{ my: 2 }} />
                <FormControlLabel
                  control={
                    <Switch
                      checked={notificationSettings.push_notifications}
                      onChange={(e) =>
                        setNotificationSettings({
                          ...notificationSettings,
                          push_notifications: e.target.checked,
                        })
                      }
                    />
                  }
                  label="Enable Push Notifications"
                  sx={{ display: 'flex', width: '100%', mb: 2 }}
                />
                <Typography variant="body2" color="text.secondary" paragraph>
                  Receive real-time notifications for important updates and alerts.
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<SaveIcon />}
                  onClick={handleSaveNotifications}
                >
                  Save Notification Settings
                </Button>
              </CardContent>
            </Card>

            <Card sx={{ mt: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Notification Frequency
                </Typography>
                <FormControl fullWidth margin="normal">
                  <InputLabel>Frequency</InputLabel>
                  <Select
                    value="immediate"
                    label="Frequency"
                  >
                    <MenuItem value="immediate">Immediate</MenuItem>
                    <MenuItem value="hourly">Hourly Digest</MenuItem>
                    <MenuItem value="daily">Daily Digest</MenuItem>
                    <MenuItem value="weekly">Weekly Digest</MenuItem>
                  </Select>
                </FormControl>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  API Configuration
                </Typography>
                <TextField
                  fullWidth
                  label="API Key"
                  value={apiSettings.api_key}
                  onChange={(e) => setApiSettings({ ...apiSettings, api_key: e.target.value })}
                  margin="normal"
                  type="password"
                  helperText="Used for API authentication"
                />
                <TextField
                  fullWidth
                  label="Webhook URL"
                  value={apiSettings.webhook_url}
                  onChange={(e) => setApiSettings({ ...apiSettings, webhook_url: e.target.value })}
                  margin="normal"
                  helperText="URL for receiving webhook notifications"
                />
                <TextField
                  fullWidth
                  label="Rate Limit (requests/hour)"
                  value={apiSettings.rate_limit}
                  onChange={(e) => setApiSettings({ ...apiSettings, rate_limit: e.target.value })}
                  margin="normal"
                  type="number"
                />
                <TextField
                  fullWidth
                  label="Cache Duration (seconds)"
                  value={apiSettings.cache_duration}
                  onChange={(e) => setApiSettings({ ...apiSettings, cache_duration: e.target.value })}
                  margin="normal"
                  type="number"
                />
                <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
                  <Button
                    variant="contained"
                    startIcon={<SaveIcon />}
                    onClick={handleSaveAPI}
                  >
                    Save API Settings
                  </Button>
                  <Button variant="outlined">
                    Regenerate API Key
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Security Settings
                </Typography>
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Two-Factor Authentication"
                  sx={{ display: 'flex', width: '100%', mb: 2 }}
                />
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="IP Whitelist"
                  sx={{ display: 'flex', width: '100%', mb: 2 }}
                />
                <FormControlLabel
                  control={<Switch />}
                  label="Session Timeout (30 min)"
                  sx={{ display: 'flex', width: '100%', mb: 2 }}
                />
                <Divider sx={{ my: 2 }} />
                <Typography variant="body2" color="text.secondary" paragraph>
                  <strong>Active Sessions:</strong>
                </Typography>
                {[
                  { device: 'Chrome on Windows', location: 'San Francisco, CA', time: '2 hours ago' },
                  { device: 'Safari on iPhone', location: 'San Francisco, CA', time: '1 day ago' },
                ].map((session, index) => (
                  <Box key={index} sx={{ py: 1, borderBottom: index < 1 ? 1 : 0, borderColor: 'divider' }}>
                    <Typography variant="body2" fontWeight="medium">
                      {session.device}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {session.location} • {session.time}
                    </Typography>
                  </Box>
                ))}
                <Button variant="outlined" color="error" sx={{ mt: 2 }}>
                  Revoke All Sessions
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={3}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Appearance
                </Typography>
                <FormControl fullWidth margin="normal">
                  <InputLabel>Theme</InputLabel>
                  <Select
                    value={displaySettings.theme}
                    label="Theme"
                    onChange={(e) =>
                      setDisplaySettings({ ...displaySettings, theme: e.target.value })
                    }
                  >
                    <MenuItem value="light">Light</MenuItem>
                    <MenuItem value="dark">Dark</MenuItem>
                    <MenuItem value="auto">System Default</MenuItem>
                  </Select>
                </FormControl>
                <FormControl fullWidth margin="normal">
                  <InputLabel>Language</InputLabel>
                  <Select
                    value={displaySettings.language}
                    label="Language"
                    onChange={(e) =>
                      setDisplaySettings({ ...displaySettings, language: e.target.value })
                    }
                  >
                    <MenuItem value="en">English</MenuItem>
                    <MenuItem value="es">Spanish</MenuItem>
                    <MenuItem value="fr">French</MenuItem>
                    <MenuItem value="de">German</MenuItem>
                  </Select>
                </FormControl>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Regional Settings
                </Typography>
                <FormControl fullWidth margin="normal">
                  <InputLabel>Timezone</InputLabel>
                  <Select
                    value={displaySettings.timezone}
                    label="Timezone"
                    onChange={(e) =>
                      setDisplaySettings({ ...displaySettings, timezone: e.target.value })
                    }
                  >
                    <MenuItem value="UTC">UTC</MenuItem>
                    <MenuItem value="America/New_York">Eastern Time</MenuItem>
                    <MenuItem value="America/Chicago">Central Time</MenuItem>
                    <MenuItem value="America/Los_Angeles">Pacific Time</MenuItem>
                    <MenuItem value="Europe/London">London</MenuItem>
                  </Select>
                </FormControl>
                <FormControl fullWidth margin="normal">
                  <InputLabel>Date Format</InputLabel>
                  <Select
                    value={displaySettings.date_format}
                    label="Date Format"
                    onChange={(e) =>
                      setDisplaySettings({ ...displaySettings, date_format: e.target.value })
                    }
                  >
                    <MenuItem value="YYYY-MM-DD">YYYY-MM-DD</MenuItem>
                    <MenuItem value="MM/DD/YYYY">MM/DD/YYYY</MenuItem>
                    <MenuItem value="DD/MM/YYYY">DD/MM/YYYY</MenuItem>
                  </Select>
                </FormControl>
                <FormControl fullWidth margin="normal">
                  <InputLabel>Currency</InputLabel>
                  <Select
                    value={displaySettings.currency}
                    label="Currency"
                    onChange={(e) =>
                      setDisplaySettings({ ...displaySettings, currency: e.target.value })
                    }
                  >
                    <MenuItem value="USD">USD ($)</MenuItem>
                    <MenuItem value="EUR">EUR (€)</MenuItem>
                    <MenuItem value="GBP">GBP (£)</MenuItem>
                    <MenuItem value="JPY">JPY (¥)</MenuItem>
                  </Select>
                </FormControl>
                <Button
                  variant="contained"
                  startIcon={<SaveIcon />}
                  onClick={handleSaveDisplay}
                  sx={{ mt: 2 }}
                >
                  Save Display Settings
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>
    </Box>
  );
}