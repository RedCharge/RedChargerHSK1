// Use the COMPAT version for broader browser support
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.22.0/firebase-app-compat.js";
import { getDatabase } from "https://www.gstatic.com/firebasejs/9.22.0/firebase-database-compat.js";

const firebaseConfig = {
  apiKey: "AIzaSyAw4CCOFDlfsVxkAcg2YdshgEB-x3fKNLY",
  authDomain: "redchargerhsk1.firebaseapp.com",
  databaseURL: "https://redchargerhsk1-default-rtdb.firebaseio.com",
  projectId: "redchargerhsk1",
  storageBucket: "redchargerhsk1.firebasestorage.app",
  messagingSenderId: "287577907928",
  appId: "1:287577907928:web:ea58eaba023213696d6dad",
  measurementId: "G-W6PDP1NWT4"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const database = getDatabase(app);