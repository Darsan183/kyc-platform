/** Main layout component with sidebar navigation */
import React, { ReactNode } from "react";
import {
  AppBar,
  Box,
  CssBaseline,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  useTheme
} from "@mui/material";
import {
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  Assignment as CasesIcon,
  Description as DocumentIcon,
  Assessment as RiskIcon,
  AccountTree as GraphIcon,
  AssignmentInd as AuditIcon,
  Notifications as MonitoringIcon,
  Logout as LogoutIcon,
  Menu as MenuIcon
} from "@mui/icons-material";
import { useRouter } from "next/router";
import Link from "next/link";
import { useAppDispatch } from "../../store/hooks";
import { logout } from "../../store/features/authSlice";

const drawerWidth = 240;

interface LayoutProps {
  children: ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const theme = useTheme();
  const router = useRouter();
  const dispatch = useAppDispatch();

  const menuItems = [
    { text: "Dashboard", icon: <DashboardIcon />, path: "/dashboard" },
    { text: "Customers", icon: <PeopleIcon />, path: "/customers" },
    { text: "KYC Cases", icon: <CasesIcon />, path: "/cases" },
    { text: "Documents", icon: <DocumentIcon />, path: "/documents" },
    { text: "Risk Assessment", icon: <RiskIcon />, path: "/risk" },
    { text: "Knowledge Graph", icon: <GraphIcon />, path: "/graph" },
    { text: "Audit Reports", icon: <AuditIcon />, path: "/audit" },
    { text: "Monitoring", icon: <MonitoringIcon />, path: "/monitoring" }
  ];

  const handleLogout = () => {
    dispatch(logout());
    router.push("/login");
  };

  return (
    <Box sx={{ display: "flex" }}>
      <CssBaseline />
      <AppBar position="fixed" sx={{ zIndex: theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            KYC Platform
          </Typography>
          <IconButton color="inherit" onClick={handleLogout}>
            <LogoutIcon />
          </IconButton>
        </Toolbar>
      </AppBar>
      <Box component="nav" sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}>
        <Drawer
          variant="permanent"
          sx={{
            "& .MuiDrawer-paper": {
              boxSizing: "border-box",
              width: drawerWidth
            }
          }}
        >
          <Toolbar />
          <List>
            {menuItems.map((item) => (
              <Link href={item.path} key={item.text} passHref>
                <ListItem disablePadding>
                  <ListItemButton selected={router.pathname === item.path}>
                    <ListItemIcon>{item.icon}</ListItemIcon>
                    <ListItemText primary={item.text} />
                  </ListItemButton>
                </ListItem>
              </Link>
            ))}
          </List>
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` }
        }}
      >
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
};