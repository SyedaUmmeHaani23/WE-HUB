// Firebase Authentication for Women Entrepreneurs Hub
import { initializeApp } from 'https://www.gstatic.com/firebasejs/11.0.2/firebase-app.js';
import { 
  getAuth, 
  signInWithRedirect, 
  signInWithPopup,
  signOut, 
  GoogleAuthProvider,
  onAuthStateChanged,
  getRedirectResult,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  sendPasswordResetEmail
} from 'https://www.gstatic.com/firebasejs/11.0.2/firebase-auth.js';

// Firebase configuration will be injected from the server
let firebaseConfig = {};
try {
  const configElement = document.getElementById('firebase-config');
  console.log('Firebase config element found:', configElement);
  
  if (configElement) {
    const apiKey = configElement.getAttribute('data-api-key');
    const projectId = configElement.getAttribute('data-project-id');
    const appId = configElement.getAttribute('data-app-id');
    
    console.log('Firebase config values:', { 
      apiKey: apiKey || 'not found',
      projectId: projectId || 'not found',
      appId: appId || 'not found'
    });
    
    firebaseConfig = {
      apiKey: apiKey,
      projectId: projectId,
      appId: appId,
      authDomain: `${projectId}.firebaseapp.com`,
      storageBucket: `${projectId}.appspot.com`,
    };
  } else {
    console.error('Firebase config element not found in the DOM');
  }
} catch (error) {
  console.error('Error loading Firebase config:', error);
}

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const googleProvider = new GoogleAuthProvider();

// Handle authentication state changes
onAuthStateChanged(auth, (user) => {
  if (user) {
    // User is signed in
    console.log('User is signed in:', user.displayName);
    
    // Get the user's ID token
    user.getIdToken().then(idToken => {
      // Send token to backend to verify and create/update user
      fetch('/auth/verify-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ idToken }),
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          console.log('User verified on backend');
          if (data.redirect) {
            window.location.href = data.redirect;
          }
        } else {
          console.error('User verification failed:', data.message);
        }
      })
      .catch(error => {
        console.error('Error sending token to backend:', error);
      });
    });
    
    // Update UI for authenticated user
    document.querySelectorAll('.unauthenticated').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.authenticated').forEach(el => el.style.display = 'block');
    
    // Set user info in UI
    document.querySelectorAll('.user-name').forEach(el => el.textContent = user.displayName || 'User');
    const userImgElements = document.querySelectorAll('.user-image');
    if (user.photoURL) {
      userImgElements.forEach(el => {
        el.src = user.photoURL;
        el.style.display = 'inline-block';
      });
    } else {
      userImgElements.forEach(el => el.style.display = 'none');
    }
  } else {
    // User is signed out
    console.log('User is signed out');
    
    // Update UI for unauthenticated user
    document.querySelectorAll('.authenticated').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.unauthenticated').forEach(el => el.style.display = 'block');
  }
});

// Handle redirect result when user is redirected back from sign-in
window.addEventListener('load', () => {
  getRedirectResult(auth)
    .then((result) => {
      if (result) {
        // User successfully signed in
        console.log('Signed in via redirect');
      }
    })
    .catch((error) => {
      console.error('Error signing in via redirect:', error);
      // Display error message to user
      const errorContainer = document.getElementById('auth-error');
      if (errorContainer) {
        errorContainer.textContent = error.message;
        errorContainer.style.display = 'block';
      }
    });
});

// Sign in with Google via redirect
window.signInWithGoogle = function() {
  signInWithRedirect(auth, googleProvider);
};

// Sign in with Google via popup
window.signInWithGooglePopup = function() {
  signInWithPopup(auth, googleProvider)
    .catch((error) => {
      console.error('Error signing in with popup:', error);
      // Display error message to user
      const errorContainer = document.getElementById('auth-error');
      if (errorContainer) {
        errorContainer.textContent = error.message;
        errorContainer.style.display = 'block';
      }
    });
};

// Sign in with email and password
window.signInWithEmail = function(email, password) {
  signInWithEmailAndPassword(auth, email, password)
    .catch((error) => {
      console.error('Error signing in with email:', error);
      // Display error message to user
      const errorContainer = document.getElementById('auth-error');
      if (errorContainer) {
        errorContainer.textContent = error.message;
        errorContainer.style.display = 'block';
      }
    });
};

// Create account with email and password
window.createAccountWithEmail = function(email, password) {
  createUserWithEmailAndPassword(auth, email, password)
    .catch((error) => {
      console.error('Error creating account:', error);
      // Display error message to user
      const errorContainer = document.getElementById('auth-error');
      if (errorContainer) {
        errorContainer.textContent = error.message;
        errorContainer.style.display = 'block';
      }
    });
};

// Reset password
window.resetPassword = function(email) {
  sendPasswordResetEmail(auth, email)
    .then(() => {
      alert('Password reset email sent! Check your inbox.');
    })
    .catch((error) => {
      console.error('Error sending reset email:', error);
      // Display error message to user
      const errorContainer = document.getElementById('auth-error');
      if (errorContainer) {
        errorContainer.textContent = error.message;
        errorContainer.style.display = 'block';
      }
    });
};

// Sign out
window.signOutUser = function() {
  signOut(auth)
    .then(() => {
      // Sign-out successful, redirect to home page
      fetch('/auth/logout', {
        method: 'POST',
      })
      .then(() => {
        window.location.href = '/';
      })
      .catch(error => {
        console.error('Error logging out on backend:', error);
        window.location.href = '/';
      });
    })
    .catch((error) => {
      console.error('Error signing out:', error);
    });
};

// Initialize auth forms
document.addEventListener('DOMContentLoaded', () => {
  // Handle email sign in form
  const signInForm = document.getElementById('sign-in-form');
  if (signInForm) {
    signInForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;
      window.signInWithEmail(email, password);
    });
  }
  
  // Handle email sign up form
  const signUpForm = document.getElementById('sign-up-form');
  if (signUpForm) {
    signUpForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const email = document.getElementById('signup-email').value;
      const password = document.getElementById('signup-password').value;
      window.createAccountWithEmail(email, password);
    });
  }
  
  // Handle password reset form
  const resetForm = document.getElementById('reset-form');
  if (resetForm) {
    resetForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const email = document.getElementById('reset-email').value;
      window.resetPassword(email);
    });
  }
});
