// Initialize Firebase
const firebaseConfig = {
  apiKey: firebaseApiKey,
  authDomain: `${firebaseProjectId}.firebaseapp.com`,
  projectId: firebaseProjectId,
  storageBucket: `${firebaseProjectId}.appspot.com`,
  messagingSenderId: "1234567890", // Will be replaced by actual value
  appId: firebaseAppId
};

// Initialize Firebase app
const app = firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();
const db = firebase.firestore();
const storage = firebase.storage();

// Set persistence to local
auth.setPersistence(firebase.auth.Auth.Persistence.LOCAL)
  .catch((error) => {
    console.error("Firebase persistence error:", error);
  });

// Google Auth Provider
const googleProvider = new firebase.auth.GoogleAuthProvider();
googleProvider.setCustomParameters({
  prompt: 'select_account'
});

// Handle auth state changes
auth.onAuthStateChanged(async (user) => {
  if (user) {
    // User is signed in
    try {
      // Get ID token
      const idToken = await user.getIdToken();
      
      // Send token to backend for verification and create session
      const response = await fetch('/auth/verify-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ idToken }),
      });
      
      const data = await response.json();
      
      if (data.success && data.redirect) {
        // Redirect to the specified URL
        window.location.href = data.redirect;
      }
    } catch (error) {
      console.error("Error during authentication:", error);
    }
  }
});

// Sign in with Google
function signInWithGoogle() {
  auth.signInWithPopup(googleProvider)
    .catch((error) => {
      console.error("Google sign-in error:", error);
      alert(`Sign-in error: ${error.message}`);
    });
}

// Sign out
function signOut() {
  auth.signOut()
    .then(() => {
      window.location.href = '/auth/logout';
    })
    .catch((error) => {
      console.error("Sign-out error:", error);
      alert(`Sign-out error: ${error.message}`);
    });
}
