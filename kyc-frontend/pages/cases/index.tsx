/** KYC Cases Page */
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
  Chip
} from "@mui/material";
import type { NextPage } from "next";
import useSWR from "swr";
import apiClient from "../../services/api";
import type { KycCase } from "../../types";

const fetcher = (url: string) => apiClient.get(url).then((res) => res.data.data);

const CasesPage: NextPage = () => {
  const { data: cases = [], error } = useSWR<KycCase[]>("/api/v1/cases", fetcher);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "COMPLETED": return "success";
      case "IN_PROGRESS": return "primary";
      case "REVIEW": return "warning";
      case "REJECTED": return "error";
      default: return "default";
    }
  };

  if (error) return <Typography>Error loading cases</Typography>;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        KYC Cases
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Case ID</TableCell>
              <TableCell>Customer</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Risk Score</TableCell>
              <TableCell>Created</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {cases.map((kycCase) => (
              <TableRow key={kycCase.id}>
                <TableCell>{kycCase.caseReference}</TableCell>
                <TableCell>{kycCase.customerName}</TableCell>
                <TableCell>
                  <Chip label={kycCase.status} color={getStatusColor(kycCase.status)} size="small" />
                </TableCell>
                <TableCell>{kycCase.riskScore || "N/A"}</TableCell>
                <TableCell>{new Date().toLocaleDateString()}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default CasesPage;