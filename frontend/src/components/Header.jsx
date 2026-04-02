import React from "react";
import { AppBar, Toolbar, Typography } from "@mui/material";
import EmojiEmotionsIcon from "@mui/icons-material/EmojiEmotions";

export default function Header() {
  return (
    <AppBar position="static" color="primary">
      <Toolbar>
        <EmojiEmotionsIcon sx={{ mr: 1 }} />
        <Typography variant="h6" fontWeight="bold">Emotion Detection System</Typography>
      </Toolbar>
    </AppBar>
  );
}
