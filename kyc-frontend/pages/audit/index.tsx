/** Audit Reports Page */
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
  Button
} from "@mui/material";
import { Download, Visibility } from "@mui/icons-material";
import type { NextPage } from "next";

const AuditPage: NextPage = () => {
  const reports = [
    { id: "RPT-001", caseId: "KYC-001", type: "Case Report", date: "2024-01-15" },
    { id: "RPT-002", caseId: "KYC-002", type: "Risk Report", date: "2024-01-16" }
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Audit Reports
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Report ID</TableCell>
              <TableCell>Case ID</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Date</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {reports.map((report) => (
              <TableRow key={report.id}>
                <TableCell>{report.id}</TableCell>
                <TableCell>{report.caseId}</TableCell>
                <TableCell>{report.type}</TableCell>
                <TableCell>{report.date}</TableCell>
                <TableCell>
                  <Button startIcon={<Visibility />} size="small">
                    View
                  </Button>
                  <Button startIcon={<Download />} size="small">
                    Download PDF
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default AuditPage;