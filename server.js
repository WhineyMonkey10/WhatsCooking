const express = require('express');
const path = require('path');
const fs = require('fs');

require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 8080;

// get all the client-safe appwrite configuration

const appwriteConfig = {
  endpoint: process.env.APPWRITE_ENDPOINT,
  project: process.env.APPWRITE_PROJECT,
  database: process.env.APPWRITE_DATABASE,
  collection: process.env.APPWRITE_PUBLIC_COLLECTION,
  deleteFunctionId: process.env.APPWRITE_ACCOUNT_DELETION_FUNCTION_ID,
};

// Serve static files
app.use(express.static(path.join(__dirname)));

// Route for the home page
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// Route for the delete page
app.get('/delete', (req, res) => {
  res.sendFile(path.join(__dirname, 'delete.html'));
});

app.get('/parameters/public', (req, res) => {
    // send back the appwrite things that are safe to be sent to the client.
    // should be sent back as a json response
    const safeConfig = Object.fromEntries(
      Object.entries(appwriteConfig).filter(([_, v]) => v !== undefined && v !== null && v !== '')
    );
    if (Object.keys(safeConfig).length !== Object.keys(appwriteConfig).length) {
      console.warn('Some appwrite env vars are missing or empty; sent subset:', safeConfig);
    } else {
      console.log('Sending appwrite config:', safeConfig);
    }
    res.json(safeConfig);
});


// Fallback route - send to index.html
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});