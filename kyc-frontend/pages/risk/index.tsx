/** Risk Assessment Page */
import React from "react";
import {
  Box,
  Paper,
  Typography,
  LinearProgress,
  Chip
} from "@mui/material";
import type { NextPage } from "next";
import type { RiskLevel } from "../../types";

const RiskPage: NextPage = () => {
  const mockRisk: RiskLevel = "medium";
  const score = 65;

  const getRiskColor = (level: RiskLevel) => {
    switch (level) {
      case "low": return "success";
      case "medium": return "warning";
      case "high": return "error";
      case "critical": return "error";
      default: return "default";
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Risk Assessment
      </Typography>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Overall Risk Score
        </Typography>
        <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
          <Box sx={{ width: "100%", mr: 2 }}>
            <LinearProgress variant="determinate" value={score} />
          </Box>
          <Typography>{score}/100</Typography>
        </Box>
        <Chip label={mockRisk.toUpperCase()} color={getRiskColor(mockRisk)} />
      </Paper>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Risk Factors
        </Typography>
        {[
          { name: "Identity Verification", score: 95, weight: 0.25 },
          { name: "AML Screening", score: 70, weight: 0.25 },
          { name: "Media Analysis", score: 80, weight: 0.20 },
          { name: "Document Verification", score: 100, weight: 0.20 },
          { name: "Compliance", score: 90, weight: 0.10 }
        ].map((factor) => (
          <Box key={factor.name} sx={{ mb: 2 }}>
            <Typography variant="body2">{factor.name}</Typography>
            <LinearProgress variant="determinate" value={factor.score} />
            <Typography variant="caption">{factor.score}% (weight: {factor.weight * 100}%)</Typography>
          </Box>
        ))}
      </Paper>
    </Box>
  );
};

export default RiskPage;