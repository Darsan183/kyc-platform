/** Redux store configuration */
import { configureStore } from "@reduxjs/toolkit";
import { authReducer } from "./features/authSlice";
import { customerReducer } from "./features/customerSlice";
import { caseReducer } from "./features/caseSlice";
import { documentReducer } from "./features/documentSlice";

export const store = configureStore({
  reducer: {
    auth: authReducer,
    customers: customerReducer,
    cases: caseReducer,
    documents: documentReducer
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false
    })
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;