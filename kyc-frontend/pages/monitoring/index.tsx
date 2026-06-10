/** Monitoring Center Page */
import React from "react";
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Chip,
  IconButton
} from "@mui/material";
import { Notifications } from "@mui/icons-material";
import type { NextPage } from "next";
import type { AlertSeverity, AlertStatus } from "../../types";

const MonitoringPage: NextPage = () => {
  const alerts = [
    {
      id: "ALERT-001",
      customerId: "CUST-001",
      severity: "high" as AlertSeverity,
      status: "open" as AlertStatus,
      summary: "New adverse media article detected"
    },
    {
      id: "ALERT-002",
      customerId: "CUST-002",
      severity: "medium" as AlertSeverity,
      status: "acknowledged" as AlertStatus,
      summary: "Sanctions list update"
    }
  ];

  const getSeverityColor = (severity: AlertSeverity) => {
    switch (severity) {
      case "critical": return "error";
      case "high": return "error";
      case "medium": return "warning";
      case "low": return "info";
      default: return "default";
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Monitoring Center
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Alert ID</TableCell>
              <TableCell>Customer</TableCell>
              <TableCell>Summary</TableCell>
              <TableCell>Severity</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {alerts.map((alert) => (
              <TableRow key={alert.id}>
                <TableCell>{alert.id}</TableCell>
                <TableCell>{alert.customerId}</TableCell>
                <TableCell>{alert.summary}</TableCell>
                <TableCell>
                  <Chip label={alert.severity} color={getSeverityColor(alert.severity)} size="small" />
                </TableCell>
                <TableCell>
                  <Chip label={alert.status} size="small" />
                </TableCell>
                <TableCell>
                  <IconButton size="small">
                    <Notifications />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default MonitoringPage;