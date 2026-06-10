/** Document Redux slice */
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import apiClient from "../../services/api";
import type { Document } from "../../types";

interface DocumentState {
  documents: Document[];
  isLoading: boolean;
  error: string | null;
}

const initialState: DocumentState = {
  documents: [],
  isLoading: false,
  error: null
};

export const fetchDocuments = createAsyncThunk(
  "documents/fetchAll",
  async (caseId: string) => {
    const response = await apiClient.get<{ data: Document[] }>(`/api/v1/documents/case/${caseId}`);
    return response.data;
  }
);

const documentSlice = createSlice({
  name: "documents",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchDocuments.fulfilled, (state, action) => {
        state.documents = action.payload;
      });
  }
});

export const documentReducer = documentSlice.reducer;