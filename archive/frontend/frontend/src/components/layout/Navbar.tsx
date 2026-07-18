import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  Menu,
  MenuItem,
  Avatar,
  useMediaQuery,
  useTheme,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Badge,
  Paper,
  Divider,
  BottomNavigation,
  BottomNavigationAction,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Notifications,
  Dashboard as DashboardIcon,
  Search as SearchIcon,
  AccountCircle,
  Logout,
  Business,
  TrendingUp,
  Description,
  Assessment,
  Close as CloseIcon,
  Settings,
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';

interface NavbarProps {
  onMenuClick: () => void;
}

export default function Navbar({ onMenuClick }: NavbarProps) {
  const { user, logout } = useAuth();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    handleClose();
  };

  const handleMobileMenuOpen = () => {
    setMobileMenuOpen(true);
  };

  const handleMobileMenuClose = () => {
    setMobileMenuOpen(false);
  };

  const mobileMenuItems = [
    { label: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
    { label: 'Competitors', icon: <Business />, path: '/competitors' },
    { label: 'Market', icon: <TrendingUp />, path: '/market' },
    { label: 'Analytics', icon: <Assessment />, path: '/analytics' },
    { label: 'Alerts', icon: <Notifications />, path: '/alerts' },
    { label: 'Reports', icon: <Description />, path: '/reports' },
    { label: 'Settings', icon: <Settings />, path: '/settings' },
  ];

  const handleMobileNavigation = (path: string) => {
    navigate(path);
    handleMobileMenuClose();
  };

  const getCurrentRoute = () => {
    const path = location.pathname;
    if (path === '/dashboard') return 0;
    if (path === '/competitors') return 1;
    if (path === '/market') return 2;
    if (path === '/analytics') return 3;
    if (path === '/alerts') return 4;
    if (path === '/reports') return 5;
    if (path === '/settings') return 6;
    return 0;
  };

  return (
    <>
      <AppBar
        position="fixed"
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 1,
          backgroundColor: '#1976d2',
        }}
      >
        <Toolbar sx={{ minHeight: { xs: 56, sm: 64 } }}>
          {isMobile ? (
            <IconButton
              edge="start"
              color="inherit"
              onClick={handleMobileMenuOpen}
              sx={{ mr: 1 }}
            >
              <MenuIcon sx={{ fontSize: 24 }} />
            </IconButton>
          ) : (
            <IconButton
              edge="start"
              color="inherit"
              onClick={onMenuClick}
              sx={{ mr: 2 }}
            >
              <MenuIcon sx={{ fontSize: 24 }} />
            </IconButton>
          )}

          <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center' }}>
            <DashboardIcon sx={{ mr: 1, fontSize: { xs: 20, sm: 24 } }} />
            <Typography
              variant="h6"
              noWrap
              component="div"
              sx={{
                fontSize: { xs: '1rem', sm: '1.25rem' },
                fontWeight: 500,
              }}
            >
              Competitive Intelligence
            </Typography>
          </Box>

          {/* Search Icon - Hidden on very small screens */}
          {!isMobile && (
            <IconButton color="inherit" sx={{ mr: 2 }}>
              <SearchIcon sx={{ fontSize: 22 }} />
            </IconButton>
          )}

          {/* Notifications with Badge */}
          <IconButton
            color="inherit"
            onClick={() => setNotificationsOpen(!notificationsOpen)}
            sx={{ mr: { xs: 1, sm: 2 } }}
          >
            <Badge badgeContent={3} color="error">
              <Notifications sx={{ fontSize: 22 }} />
            </Badge>
          </IconButton>

          {/* User Menu */}
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <IconButton
              size="large"
              aria-label="account of current user"
              aria-controls="menu-appbar"
              aria-haspopup="true"
              onClick={handleMenu}
              color="inherit"
            >
              <Avatar
                sx={{
                  width: { xs: 32, sm: 40 },
                  height: { xs: 32, sm: 40 },
                  bgcolor: '#ffffff',
                  color: '#1976d2',
                  fontSize: { xs: '0.875rem', sm: '1rem' },
                }}
              >
                {user?.username?.charAt(0).toUpperCase() || 'U'}
              </Avatar>
            </IconButton>
            <Menu
              id="menu-appbar"
              anchorEl={anchorEl}
              anchorOrigin={{
                vertical: 'bottom',
                horizontal: 'right',
              }}
              keepMounted
              transformOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              open={Boolean(anchorEl)}
              onClose={handleClose}
              sx={{
                '& .MuiPaper-root': {
                  minWidth: { xs: 200, sm: 240 },
                },
              }}
            >
              <MenuItem disabled>
                <Box sx={{ py: 1, px: 1 }}>
                  <Typography variant="subtitle2" fontWeight="bold">
                    {user?.full_name || 'User'}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {user?.email || ''}
                  </Typography>
                </Box>
              </MenuItem>
              <Divider />
              <MenuItem onClick={handleClose}>
                <ListItemIcon>
                  <AccountCircle fontSize="small" />
                </ListItemIcon>
                <ListItemText>Profile</ListItemText>
              </MenuItem>
              <MenuItem onClick={handleClose}>
                <ListItemIcon>
                  <Settings fontSize="small" />
                </ListItemIcon>
                <ListItemText>Settings</ListItemText>
              </MenuItem>
              <Divider />
              <MenuItem onClick={handleLogout}>
                <ListItemIcon>
                  <Logout fontSize="small" />
                </ListItemIcon>
                <ListItemText>Logout</ListItemText>
              </MenuItem>
            </Menu>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Mobile Menu Drawer */}
      <Drawer
        anchor="left"
        open={mobileMenuOpen}
        onClose={handleMobileMenuClose}
        sx={{
          '& .MuiDrawer-paper': {
            width: 280,
          },
        }}
      >
        <Box
          sx={{
            p: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <Typography variant="h6" fontWeight="bold">
            Menu
          </Typography>
          <IconButton onClick={handleMobileMenuClose}>
            <CloseIcon />
          </IconButton>
        </Box>
        <Divider />
        <List>
          {mobileMenuItems.map((item) => (
            <ListItem
              button
              key={item.label}
              onClick={() => handleMobileNavigation(item.path)}
              selected={location.pathname === item.path}
              sx={{
                '&.Mui-selected': {
                  backgroundColor: 'rgba(25, 118, 210, 0.1)',
                  '&:hover': {
                    backgroundColor: 'rgba(25, 118, 210, 0.15)',
                  },
                },
              }}
            >
              <ListItemIcon>
                {item.label === 'Alerts' ? (
                  <Badge badgeContent={3} color="error">
                    {item.icon}
                  </Badge>
                ) : (
                  item.icon
                )}
              </ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItem>
          ))}
        </List>
      </Drawer>

      {/* Mobile Bottom Navigation */}
      {isMobile && (
        <Paper
          sx={{
            position: 'fixed',
            bottom: 0,
            left: 0,
            right: 0,
            zIndex: (theme) => theme.zIndex.drawer + 2,
            display: { xs: 'block', sm: 'none' },
          }}
          elevation={3}
        >
          <BottomNavigation
            value={getCurrentRoute()}
            onChange={(event, newValue) => {
              if (newValue < mobileMenuItems.length) {
                navigate(mobileMenuItems[newValue].path);
              }
            }}
            showLabels
          >
            <BottomNavigationAction
              label="Home"
              icon={<DashboardIcon />}
              sx={{
                minWidth: 0,
                '& .MuiBottomNavigationAction-label': {
                  fontSize: '0.7rem',
                },
              }}
            />
            <BottomNavigationAction
              label="Competitors"
              icon={<Business />}
              sx={{
                minWidth: 0,
                '& .MuiBottomNavigationAction-label': {
                  fontSize: '0.7rem',
                },
              }}
            />
            <BottomNavigationAction
              label="Market"
              icon={<TrendingUp />}
              sx={{
                minWidth: 0,
                '& .MuiBottomNavigationAction-label': {
                  fontSize: '0.7rem',
                },
              }}
            />
            <BottomNavigationAction
              label="Analytics"
              icon={<Assessment />}
              sx={{
                minWidth: 0,
                '& .MuiBottomNavigationAction-label': {
                  fontSize: '0.7rem',
                },
              }}
            />
            <BottomNavigationAction
              label="Alerts"
              icon={<Badge badgeContent={3} color="error"><Notifications /></Badge>}
              sx={{
                minWidth: 0,
                '& .MuiBottomNavigationAction-label': {
                  fontSize: '0.7rem',
                },
              }}
            />
          </BottomNavigation>
        </Paper>
      )}
    </>
  );
}