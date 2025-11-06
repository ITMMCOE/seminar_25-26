// import axios from 'axios';

// const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// const api = axios.create({
//   baseURL: API_URL,
// });

// // Add token to requests
// api.interceptors.request.use(
//   (config) => {
//     const token = localStorage.getItem('token');
//     if (token) {
//       config.headers.Authorization = `Bearer ${token}`;
//     }
//     return config;
//   },
//   (error) => {
//     return Promise.reject(error);
//   }
// );

// export default api;

import axios from 'axios';

// This uses the URL from your .env file, with a fallback for local development.
// Ensure your .env file has REACT_APP_BACKEND_URL=http://127.0.0.1:8000
const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_URL,
});

// This part automatically adds the user's authentication token to every request
// after they have logged in.
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      // The backend expects the token in this "Bearer <token>" format.
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api;
