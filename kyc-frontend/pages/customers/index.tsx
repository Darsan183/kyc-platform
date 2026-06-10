/** Customers List Page */
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
  IconButton,
  Tooltip
} from "@mui/material";
import { Visibility, Edit, Delete } from "@mui/icons-material";
import type { NextPage } from "next";
import useSWR from "swr";
import apiClient from "../../services/api";
import type { Customer } from "../../types";
import { Layout } from "../../components/layout/Layout";

const fetcher = (url: string) => apiClient.get(url).then((res) => res.data.data);

const CustomersPage: NextPage = () => {
  const { data: customers = [], error } = useSWR<Customer[]>("/api/v1/customers", fetcher);

  if (error) return <Typography>Error loading customers</Typography>;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Customers
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Phone</TableCell>
              <TableCell>Country</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {customers.map((customer) => (
              <TableRow key={customer.id}>
                <TableCell>{customer.customerReference}</TableCell>
                <TableCell>{customer.firstName} {customer.lastName}</TableCell>
                <TableCell>{customer.email}</TableCell>
                <TableCell>{customer.phone}</TableCell>
                <TableCell>{customer.country}</TableCell>
                <TableCell>
                  <Tooltip title="View">
                    <IconButton size="small">
                      <Visibility />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Edit">
                    <IconButton size="small">
                      <Edit />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default CustomersPage;