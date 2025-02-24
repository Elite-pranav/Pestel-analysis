import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:5000", // Replace with your Flask backend URL if different
  headers: {
    "Content-Type": "application/json",
  },
});

export default api;
