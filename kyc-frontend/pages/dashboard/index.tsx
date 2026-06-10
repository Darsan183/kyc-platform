/** Dashboard Page */
import React from "react";
import { Box, Grid, Paper, Typography } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from "recharts";
import { useAppSelector } from "../../store/hooks";
import type { NextPage } from "next";

interface StatCardProps {
  title: string;
  value: string | number;
  color?: "primary" | "secondary" | "error" | "info" | "success" | "warning";
}

const StatCard: React.FC<StatCardProps> = ({ title, value, color = "primary" }) => {
  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="subtitle2" color="text.secondary">
        {title}
      </Typography>
      <Typography variant="h4">{value}</Typography>
    </Paper>
  );
};

const DashboardPage: NextPage = () => {
  const theme = useTheme();

  const chartData = [
    { name: "Mon", cases: 12 },
    { name: "Tue", cases: 19 },
    { name: "Wed", cases: 3 },
    { name: "Thu", cases: 5 },
    { name: "Fri", cases: 22 },
    { name: "Sat", cases: 8 },
    { name: "Sun", cases: 15 }
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Total Customers" value="1,248" color="primary" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Active Cases" value="245" color="secondary" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="High Risk Cases" value="24" color="error" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Pending Reviews" value="12" color="warning" />
        </Grid>
      </Grid>

      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Cases by Day
        </Typography>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="cases" fill={theme.palette.primary.main} />
          </BarChart>
        </ResponsiveContainer>
      </Paper>
    </Box>
  );
};

export default DashboardPage;