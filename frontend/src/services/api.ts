import axios from "axios";

const baseURL =
  import.meta.env.VITE_API_URL ?? `http://${window.location.hostname}:8000/api`;

export const api = axios.create({
  baseURL,
  withCredentials: true,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const path = window.location.pathname;
    const emAreaAdministrativa = path.startsWith("/admin");
    if (error.response?.status === 401 && emAreaAdministrativa) {
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);
