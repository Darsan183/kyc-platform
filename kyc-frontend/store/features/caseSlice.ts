/** Case Redux slice */
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import apiClient from "../../services/api";
import type { KycCase } from "../../types";

interface CaseState {
  cases: KycCase[];
  isLoading: boolean;
  error: string | null;
}

const initialState: CaseState = {
  cases: [],
  isLoading: false,
  error: null
};

export const fetchCases = createAsyncThunk(
  "cases/fetchAll",
  async () => {
    const response = await apiClient.get<{ data: KycCase[] }>("/api/v1/cases");
    return response.data;
  }
);

const caseSlice = createSlice({
  name: "cases",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchCases.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(fetchCases.fulfilled, (state, action) => {
        state.isLoading = false;
        state.cases = action.payload;
      })
      .addCase(fetchCases.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || "Failed to fetch cases";
      });
  }
});

export const caseReducer = caseSlice.reducer;