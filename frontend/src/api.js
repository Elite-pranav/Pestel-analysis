import axios from "axios";

const api = axios.create({
  baseURL: "https://pestel-analysis-production.up.railway.app", // Use the deployed backend URL
  headers: {
    "Content-Type": "application/json",
     timeout: 30000, // Set timeout to 30s (increase if needed)

  },
});

export default api;
