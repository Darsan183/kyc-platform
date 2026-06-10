/** Customer Redux slice */
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import apiClient from "../../services/api";
import type { Customer } from "../../types";

interface CustomerState {
  customers: Customer[];
  isLoading: boolean;
  error: string | null;
}

const initialState: CustomerState = {
  customers: [],
  isLoading: false,
  error: null
};

export const fetchCustomers = createAsyncThunk(
  "customers/fetchAll",
  async () => {
    const response = await apiClient.get<{ data: Customer[] }>("/api/v1/customers");
    return response.data;
  }
);

const customerSlice = createSlice({
  name: "customers",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchCustomers.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(fetchCustomers.fulfilled, (state, action) => {
        state.isLoading = false;
        state.customers = action.payload;
      })
      .addCase(fetchCustomers.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || "Failed to fetch customers";
      });
  }
});

export const customerReducer = customerSlice.reducer;