// Profile update functionality
document.addEventListener('DOMContentLoaded', function() {
  const profileForm = document.getElementById('profile-form');
  
  if (profileForm) {
    profileForm.addEventListener('submit', function(e) {
      // Form will be submitted normally to the server
      // Additional client-side validation can be added here
      
      // Show loading state
      const submitButton = profileForm.querySelector('button[type="submit"]');
      if (submitButton) {
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';
      }
    });
  }
  
  // Password reset functionality
  const resetPasswordButton = document.getElementById('reset-password');
  if (resetPasswordButton) {
    resetPasswordButton.addEventListener('click', function(e) {
      e.preventDefault();
      
      const email = resetPasswordButton.dataset.email;
      if (!email) {
        alert('No email address found. Please contact support.');
        return;
      }
      
      auth.sendPasswordResetEmail(email)
        .then(() => {
          alert('Password reset email sent. Please check your inbox.');
        })
        .catch((error) => {
          console.error("Password reset error:", error);
          alert(`Error: ${error.message}`);
        });
    });
  }
});

// Functions for login/register pages
function handleLogin(e) {
  e.preventDefault();
  
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  
  // Show loading state
  const submitButton = document.querySelector('button[type="submit"]');
  submitButton.disabled = true;
  submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Logging in...';
  
  auth.signInWithEmailAndPassword(email, password)
    .catch((error) => {
      console.error("Login error:", error);
      // Reset button state
      submitButton.disabled = false;
      submitButton.textContent = 'Log In';
      
      // Show error message
      const errorContainer = document.getElementById('login-error');
      if (errorContainer) {
        errorContainer.textContent = error.message;
        errorContainer.classList.remove('d-none');
      }
    });
}

function handleRegister(e) {
  e.preventDefault();
  
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  const confirmPassword = document.getElementById('confirm-password').value;
  const displayName = document.getElementById('display-name').value;
  
  // Validate form
  const errorContainer = document.getElementById('register-error');
  if (password !== confirmPassword) {
    errorContainer.textContent = 'Passwords do not match';
    errorContainer.classList.remove('d-none');
    return;
  }
  
  if (password.length < 6) {
    errorContainer.textContent = 'Password must be at least 6 characters long';
    errorContainer.classList.remove('d-none');
    return;
  }
  
  // Show loading state
  const submitButton = document.querySelector('button[type="submit"]');
  submitButton.disabled = true;
  submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Creating account...';
  
  // Create user
  auth.createUserWithEmailAndPassword(email, password)
    .then((userCredential) => {
      // Update profile with display name
      return userCredential.user.updateProfile({
        displayName: displayName
      });
    })
    .catch((error) => {
      console.error("Registration error:", error);
      // Reset button state
      submitButton.disabled = false;
      submitButton.textContent = 'Create Account';
      
      // Show error message
      if (errorContainer) {
        errorContainer.textContent = error.message;
        errorContainer.classList.remove('d-none');
      }
    });
}
