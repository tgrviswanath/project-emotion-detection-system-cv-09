import React, { useState, useRef } from "react";
import {
  Box, CircularProgress, Alert, Typography, Paper,
  Chip, Grid, Divider,
} from "@mui/material";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import { detectEmotion } from "../services/emotionApi";

const EMOTION_COLORS = {
  happy: "#4caf50", sad: "#2196f3", angry: "#f44336",
  surprise: "#ff9800", fear: "#9c27b0", disgust: "#795548", neutral: "#9e9e9e",
};

const EMOTION_EMOJI = {
  happy: "😊", sad: "😢", angry: "😠",
  surprise: "😲", fear: "😨", disgust: "🤢", neutral: "😐",
};

export default function EmotionPage() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const fileRef = useRef();

  const handleFile = async (file) => {
    if (!file) return;
    setLoading(true); setError(""); setResult(null);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const r = await detectEmotion(fd);
      setResult(r.data);
    } catch (e) {
      setError(e.response?.data?.detail || "Detection failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Paper
        variant="outlined"
        onClick={() => fileRef.current.click()}
        onDrop={(e) => { e.preventDefault(); handleFile(e.dataTransfer.files[0]); }}
        onDragOver={(e) => e.preventDefault()}
        sx={{ p: 3, mb: 2, textAlign: "center", cursor: "pointer", borderStyle: "dashed", "&:hover": { bgcolor: "action.hover" } }}
      >
        <input ref={fileRef} type="file" hidden accept=".jpg,.jpeg,.png,.bmp,.webp"
          onChange={(e) => handleFile(e.target.files[0])} />
        {loading
          ? <Box><CircularProgress size={28} sx={{ mb: 1 }} /><Typography color="text.secondary">Analyzing emotions…</Typography></Box>
          : <Box sx={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 1 }}>
              <UploadFileIcon color="action" />
              <Typography color="text.secondary">Drag & drop or click — JPG / PNG / BMP / WEBP</Typography>
            </Box>
        }
      </Paper>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {result && (
        <Box>
          <Box sx={{ display: "flex", gap: 1.5, mb: 2, flexWrap: "wrap" }}>
            <Chip label={`${result.face_count} face${result.face_count !== 1 ? "s" : ""} detected`}
              color={result.face_count > 0 ? "success" : "default"} />
            <Chip label={`${result.image_width} × ${result.image_height} px`} variant="outlined" size="small" />
          </Box>

          <Paper variant="outlined" sx={{ p: 1, mb: 2 }}>
            <img src={`data:image/jpeg;base64,${result.annotated_image}`}
              alt="annotated" style={{ width: "100%", borderRadius: 4 }} />
          </Paper>

          {result.faces.length > 0 && (
            <>
              <Divider sx={{ mb: 2 }} />
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>Emotion Analysis</Typography>
              <Grid container spacing={2}>
                {result.faces.map((face, i) => {
                  const chartData = Object.entries(face.emotions)
                    .sort((a, b) => b[1] - a[1])
                    .map(([emotion, score]) => ({ emotion: `${EMOTION_EMOJI[emotion] || ""} ${emotion}`, score }));
                  return (
                    <Grid item xs={12} sm={6} key={i}>
                      <Paper variant="outlined" sx={{ p: 2 }}>
                        <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1.5 }}>
                          <Typography variant="h4">{EMOTION_EMOJI[face.dominant_emotion] || "😐"}</Typography>
                          <Box>
                            <Typography variant="subtitle2">Face {i + 1}</Typography>
                            <Chip label={face.dominant_emotion}
                              size="small"
                              sx={{ bgcolor: EMOTION_COLORS[face.dominant_emotion], color: "white" }} />
                          </Box>
                        </Box>
                        <ResponsiveContainer width="100%" height={200}>
                          <BarChart data={chartData} layout="vertical"
                            margin={{ top: 0, right: 30, bottom: 0, left: 80 }}>
                            <XAxis type="number" domain={[0, 100]} unit="%" tick={{ fontSize: 11 }} />
                            <YAxis type="category" dataKey="emotion" tick={{ fontSize: 11 }} width={80} />
                            <Tooltip formatter={(v) => `${v}%`} />
                            <Bar dataKey="score" radius={[0, 4, 4, 0]}>
                              {chartData.map((d, ci) => (
                                <Cell key={ci}
                                  fill={EMOTION_COLORS[d.emotion.split(" ")[1]] || "#9e9e9e"} />
                              ))}
                            </Bar>
                          </BarChart>
                        </ResponsiveContainer>
                      </Paper>
                    </Grid>
                  );
                })}
              </Grid>
            </>
          )}

          {result.face_count === 0 && (
            <Alert severity="info">No faces detected. Try a clearer photo with visible faces.</Alert>
          )}
        </Box>
      )}
    </Box>
  );
}
