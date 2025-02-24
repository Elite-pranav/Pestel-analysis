import React, { useState } from "react";
import api from "../api";
import {
  Container,
  Box,
  TextField,
  Button,
  Typography,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Card,
  CardContent,
} from "@mui/material";

const PestelForm = ({ onResults }) => {
  const [formData, setFormData] = useState({
    business_name: "",
    industry: "",
    geographical_focus: "",
    time_frame: "Short-term",
    target_market: "",
    competitors: "",
    political_factors: {}, // ✅ Changed from list to dictionary
  });

  const politicalOptions = [
    "Government Policies",
    "Political Stability",
    "Tax Regulations",
    "Industry Regulations",
    "Global Trade Agreements",
  ];

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleCheckboxChange = (e) => {
    const { name, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      political_factors: {
        ...prev.political_factors,
        [name]: checked, // ✅ Store as a dictionary { "Government Policies": true, "Tax Regulations": false }
      },
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
  
    try {
      const response = await api.post("/analyze_pestel", formData);
      console.log("✅ API Response:", response.data);
  
      // Fetch the generated summary after analysis is complete
      const summaryResponse = await api.get(`/get_summary/${formData.business_name}`);
      
      if (summaryResponse.data.error) {
        console.error("❌ Error fetching summary:", summaryResponse.data.error);
      } else {
        onResults(summaryResponse.data);
      }
    } catch (error) {
      console.error("❌ Error submitting form:", error);
    }
  };

  return (
    <Container maxWidth="sm">
      <Card sx={{ mt: 5, p: 3, boxShadow: 5, borderRadius: 4, backgroundColor: "#f5f5f5" }}>
        <CardContent>
          <Typography
            variant="h4"
            align="center"
            gutterBottom
            sx={{
              fontWeight: "bold",
              background: "linear-gradient(90deg, #ff4081, #ff9800)",
              WebkitBackgroundClip: "text",
              color: "transparent",
            }}
          >
            PESTEL Analysis Tool
          </Typography>

          <form onSubmit={handleSubmit}>
            <Box mb={2}>
              <TextField fullWidth label="Business Name" name="business_name" onChange={handleChange} required />
            </Box>
            <Box mb={2}>
              <TextField fullWidth label="Industry" name="industry" onChange={handleChange} required />
            </Box>
            <Box mb={2}>
              <TextField fullWidth label="Geographical Focus" name="geographical_focus" onChange={handleChange} required />
            </Box>
            <Box mb={2}>
              <TextField fullWidth label="Target Market" name="target_market" onChange={handleChange} required />
            </Box>
            <Box mb={2}>
              <TextField fullWidth label="Competitors (comma-separated)" name="competitors" onChange={handleChange} />
            </Box>

            <Box mb={2}>
              <FormControl fullWidth>
                <InputLabel>Time Frame</InputLabel>
                <Select name="time_frame" value={formData.time_frame} onChange={handleChange}>
                  <MenuItem value="Short-term">Short-term</MenuItem>
                  <MenuItem value="Long-term">Long-term</MenuItem>
                </Select>
              </FormControl>
            </Box>

            <Typography variant="h6" gutterBottom>Political Factors:</Typography>
            <FormGroup>
              {politicalOptions.map((option) => (
                <FormControlLabel
                  key={option}
                  control={
                    <Checkbox
                      name={option}
                      checked={formData.political_factors[option] || false}
                      onChange={handleCheckboxChange}
                    />
                  }
                  label={option}
                />
              ))}
            </FormGroup>

            <Button
              type="submit"
              variant="contained"
              color="secondary"
              fullWidth
              sx={{
                mt: 3,
                background: "linear-gradient(45deg, #ff4081, #ff9800)",
                color: "#fff",
                fontWeight: "bold",
                "&:hover": {
                  background: "linear-gradient(45deg, #ff1744, #ff9100)",
                },
              }}
            >
              🚀 Submit
            </Button>
          </form>
        </CardContent>
      </Card>
    </Container>
  );
};

export default PestelForm;
