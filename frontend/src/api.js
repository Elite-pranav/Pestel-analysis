import axios from "axios";

const api = axios.create({
  baseURL: "https://pestel-analysis-production.up.railway.app", // Use the deployed backend URL
  headers: {
    "Content-Type": "application/json",
  },
});

export default api;
