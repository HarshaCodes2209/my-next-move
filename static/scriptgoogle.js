
  import { initializeApp } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-app.js";
  import { getAnalytics } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-analytics.js";
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/11.1.0/firebase-auth.js";
  const firebaseConfig = {
    apiKey: "AIzaSyC8d5ArdsgHd7ClO-keFoHP-T4DQPPZrIc",
    authDomain: "fir-79177.firebaseapp.com",
    projectId: "fir-79177",
    storageBucket: "fir-79177.firebasestorage.app",
    messagingSenderId: "122328527479",
    appId: "1:122328527479:web:e7b8222e9bf6c2d6bb4c72",
    measurementId: "G-1MXV40C2XT"
  };
  const app = initializeApp(firebaseConfig);
  const analytics = getAnalytics(app);