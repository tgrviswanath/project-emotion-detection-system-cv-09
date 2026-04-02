import axios from "axios";
const api = axios.create({ baseURL: process.env.REACT_APP_API_URL || "http://localhost:8000" });
export const detectEmotion = (fd) =>
  api.post("/api/v1/emotion", fd, { headers: { "Content-Type": "multipart/form-data" } });
