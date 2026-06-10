/** Documents Page */
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
import { Visibility, Download } from "@mui/icons-material";
import type { NextPage } from "next";
import type { VerificationStatus } from "../../types";

const DocumentsPage: NextPage = () => {
  const documents = [
    {
      id: "DOC-001",
      documentReference: "PASSPORT-001",
      caseId: "KYC-001",
      type: "PASSPORT",
      status: "VERIFIED" as VerificationStatus
    },
    {
      id: "DOC-002",
      documentReference: "UTILITY-001",
      caseId: "KYC-001",
      type: "UTILITY_BILL",
      status: "PENDING" as VerificationStatus
    }
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Documents
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Document ID</TableCell>
              <TableCell>Case ID</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {documents.map((doc) => (
              <TableRow key={doc.id}>
                <TableCell>{doc.documentReference}</TableCell>
                <TableCell>{doc.caseId}</TableCell>
                <TableCell>{doc.type}</TableCell>
                <TableCell>
                  <Chip label={doc.status} color={doc.status === "VERIFIED" ? "success" : "warning"} size="small" />
                </TableCell>
                <TableCell>
                  <IconButton size="small"><Visibility /></IconButton>
                  <IconButton size="small"><Download /></IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default DocumentsPage;