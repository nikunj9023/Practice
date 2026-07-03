import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  user: null,
  token: null,
  refreshToken: null,
  isAuthenticated: false,
  status: 'idle', // 'idle' | 'loading' | 'succeeded' | 'failed'
  error: null
};

// We create a basic slice for Auth.
// Async thunks (e.g. for login API calls) can be added here or in a separate file.
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setCredentials: (state, action) => {
      const { user, token, refreshToken } = action.payload;
      state.user = user;
      state.token = token;
      state.refreshToken = refreshToken;
      state.isAuthenticated = true;
      state.error = null;
      
      // Optionally persist tokens to localStorage (though HttpOnly cookies are safer)
      localStorage.setItem('token', token);
      if (refreshToken) {
        localStorage.setItem('refreshToken', refreshToken);
      }
    },
    logout: (state) => {
      state.user = null;
      state.token = null;
      state.refreshToken = null;
      state.isAuthenticated = false;
      
      // Clear persistence
      localStorage.removeItem('token');
      localStorage.removeItem('refreshToken');
    },
    setAuthLoading: (state, action) => {
      state.status = action.payload ? 'loading' : 'idle';
    },
    setAuthError: (state, action) => {
      state.status = 'failed';
      state.error = action.payload;
    }
  }
});

export const { setCredentials, logout, setAuthLoading, setAuthError } = authSlice.actions;

// Selectors
export const selectCurrentUser = (state) => state.auth.user;
export const selectCurrentToken = (state) => state.auth.token;
export const selectIsAuthenticated = (state) => state.auth.isAuthenticated;

export default authSlice.reducer;
