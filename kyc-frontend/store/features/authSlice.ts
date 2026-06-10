/** Authentication Redux slice */
import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import { AuthResponse, LoginRequest, User } from "../../types";
import apiClient from "../../services/api";

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: AuthState = {
  user: null,
  token: typeof window !== "undefined" ? localStorage.getItem("token") : null,
  isLoading: false,
  error: null
};

export const login = createAsyncThunk<AuthResponse, LoginRequest>(
  "auth/login",
  async (credentials, { rejectWithValue }) => {
    try {
      const response = await apiClient.post<AuthResponse>("/api/v1/auth/login", credentials);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.message || "Login failed");
    }
  }
);

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    logout: (state) => {
      state.user = null;
      state.token = null;
      if (typeof window !== "undefined") {
        localStorage.removeItem("token");
      }
    },
    setCredentials: (state, action: PayloadAction<{ user: User; token: string }>) => {
      state.user = action.payload.user;
      state.token = action.payload.token;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.isLoading = false;
        state.token = action.payload.accessToken;
        state.user = {
          id: action.payload.userId,
          username: action.payload.username,
          email: action.payload.email,
          firstName: "",
          lastName: "",
          roles: action.payload.roles,
          enabled: true
        };
        if (typeof window !== "undefined") {
          localStorage.setItem("token", action.payload.accessToken);
        }
      })
      .addCase(login.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  }
});

export const { logout, setCredentials } = authSlice.actions;
export const authReducer = authSlice.reducer;