import React from "react";
import { Typography, Container, Card, CardContent, List, ListItem } from "@mui/material";

const ResultsDisplay = ({ results }) => {
  if (!results || Object.keys(results).length === 0) {
    return (
      <Typography variant="h6" align="center" sx={{ mt: 4, color: "gray" }}>
        No results yet. Submit the form above.
      </Typography>
    );
  }

  // Split summary into points
  const summaryPoints = results.summary.split("\n").filter(point => point.trim() !== "");

  return (
    <Container sx={{ mt: 5 }}>
      {/* Main Summary Heading */}
      <Typography variant="h5" align="center" fontWeight="bold" gutterBottom>
        Political Analysis Summary
      </Typography>

      <Card sx={{ mb: 2, p: 2, backgroundColor: "#f5f5f5", boxShadow: 3 }}>
        <CardContent>
          <List>
            {summaryPoints.map((point, index) => {
              // Identify section headings and render them separately
              const formattedPoint = point.replace(/[#*]/g, "").trim(); // Remove # and * if any exist

              if (
                formattedPoint === "Political Analysis Summary" ||
                formattedPoint === "2. Political Factor Analysis" ||
                formattedPoint === "Political Factor Analysis" ||
                formattedPoint === "Government Policies:" ||
                formattedPoint === "Political Stability:" ||
                formattedPoint === "Tax Regulations:" ||
                formattedPoint === "Industry Regulations:" ||
                formattedPoint === "Political Stability:" ||
                formattedPoint === "Industry Regulations:" ||
                formattedPoint === "Summary" ||
                formattedPoint === "1. Summary" ||
                formattedPoint === "Political Factor Analysis" ||
                formattedPoint === "Government Policies" ||
                formattedPoint === "Political Stability" ||
                formattedPoint === "Tax Regulations" ||
                formattedPoint === "Industry Regulations" ||
                formattedPoint === "Political Stability" ||
                formattedPoint === "Industry Regulations" ||
                formattedPoint === "Summary"

              ) {
                return (
                  <Typography
                    key={index}
                    variant="h6"
                    align="center"
                    fontWeight="bold"
                    sx={{ mt: 2, mb: 1 }}
                  >
                    {formattedPoint}
                  </Typography>
                );
              }

              return (
                <ListItem key={index} sx={{ display: "list-item", listStyleType: "disc", ml: 2 }}>
                  <Typography variant="body1">{formattedPoint}</Typography>
                </ListItem>
              );
            })}
          </List>
        </CardContent>
      </Card>
    </Container>
  );
};

export default ResultsDisplay;
