document.addEventListener('DOMContentLoaded', function() {
  // Forum post form
  const forumForm = document.getElementById('forum-post-form');
  if (forumForm) {
    forumForm.addEventListener('submit', function(e) {
      // Form will be submitted normally to the server
      // Additional client-side validation can be added here
      
      // Check if title and content are not empty
      const title = document.getElementById('post-title').value.trim();
      const content = document.getElementById('post-content').value.trim();
      
      if (!title || !content) {
        e.preventDefault();
        alert('Please fill in both title and content for your post.');
        return;
      }
      
      // Show loading state
      const submitButton = forumForm.querySelector('button[type="submit"]');
      if (submitButton) {
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Posting...';
      }
    });
  }
  
  // Comment submission
  const commentForm = document.getElementById('comment-form');
  if (commentForm) {
    commentForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const postId = commentForm.dataset.postId;
      const content = document.getElementById('comment-content').value.trim();
      
      if (!content) {
        alert('Comment cannot be empty.');
        return;
      }
      
      // Show loading state
      const submitButton = commentForm.querySelector('button[type="submit"]');
      submitButton.disabled = true;
      submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Submitting...';
      
      // Submit comment via AJAX
      fetch(`/community/forum/post/${postId}/comment`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content })
      })
      .then(response => response.json())
      .then(data => {
        // Reset button state
        submitButton.disabled = false;
        submitButton.textContent = 'Post Comment';
        
        if (data.success) {
          // Clear comment input
          document.getElementById('comment-content').value = '';
          
          // Add comment to the list
          addCommentToList(data.comment);
        } else {
          alert(`Error: ${data.message}`);
        }
      })
      .catch(error => {
        console.error('Error submitting comment:', error);
        alert('Error submitting comment. Please try again.');
        
        // Reset button state
        submitButton.disabled = false;
        submitButton.textContent = 'Post Comment';
      });
    });
    
    // Function to add comment to the list
    function addCommentToList(comment) {
      const commentsContainer = document.getElementById('comments-container');
      const commentElement = document.createElement('div');
      commentElement.className = 'card mb-3';
      
      // Format date
      const date = new Date(comment.created_at);
      const formattedDate = date.toLocaleString();
      
      commentElement.innerHTML = `
        <div class="card-body">
          <div class="d-flex align-items-center mb-2">
            <img src="${comment.author.photo_url || '/static/img/default-avatar.svg'}" class="rounded-circle me-2" width="40" height="40" alt="User avatar">
            <div>
              <h5 class="card-title mb-0">${comment.author.display_name}</h5>
              <small class="text-muted">${formattedDate}</small>
            </div>
          </div>
          <p class="card-text">${comment.content}</p>
        </div>
      `;
      
      commentsContainer.appendChild(commentElement);
      
      // Scroll to the new comment
      commentElement.scrollIntoView({ behavior: 'smooth' });
    }
  }
  
  // Event form
  const eventForm = document.getElementById('event-form');
  if (eventForm) {
    const isVirtualCheckbox = document.getElementById('is-virtual');
    const meetingLinkField = document.getElementById('meeting-link-group');
    
    // Toggle meeting link field based on is_virtual checkbox
    if (isVirtualCheckbox && meetingLinkField) {
      isVirtualCheckbox.addEventListener('change', function() {
        if (this.checked) {
          meetingLinkField.classList.remove('d-none');
        } else {
          meetingLinkField.classList.add('d-none');
        }
      });
      
      // Initial state
      if (isVirtualCheckbox.checked) {
        meetingLinkField.classList.remove('d-none');
      } else {
        meetingLinkField.classList.add('d-none');
      }
    }
    
    eventForm.addEventListener('submit', function(e) {
      // Form will be submitted normally to the server
      // Additional client-side validation can be added here
      
      // Validate date and time
      const date = document.getElementById('event-date').value;
      const time = document.getElementById('event-time').value;
      
      if (new Date(`${date}T${time}`) < new Date()) {
        e.preventDefault();
        alert('Event date and time must be in the future.');
        return;
      }
      
      // Validate meeting link for virtual events
      if (isVirtualCheckbox && isVirtualCheckbox.checked) {
        const meetingLink = document.getElementById('meeting-link').value.trim();
        if (!meetingLink) {
          e.preventDefault();
          alert('Please provide a meeting link for virtual events.');
          return;
        }
      }
      
      // Show loading state
      const submitButton = eventForm.querySelector('button[type="submit"]');
      if (submitButton) {
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Creating Event...';
      }
    });
  }
  
  // Add to calendar button
  const addToCalendarButtons = document.querySelectorAll('.add-to-calendar');
  addToCalendarButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      
      const eventTitle = this.dataset.eventTitle;
      const eventDate = this.dataset.eventDate;
      const eventTime = this.dataset.eventTime;
      const eventLocation = this.dataset.eventLocation;
      const eventDescription = this.dataset.eventDescription;
      
      // Generate Google Calendar URL
      const startDate = new Date(`${eventDate}T${eventTime}`);
      const endDate = new Date(startDate.getTime() + 60 * 60 * 1000); // 1 hour later
      
      const formatDate = (date) => {
        return date.toISOString().replace(/-|:|\.\d+/g, '');
      };
      
      const googleCalendarUrl = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${encodeURIComponent(eventTitle)}&dates=${formatDate(startDate)}/${formatDate(endDate)}&details=${encodeURIComponent(eventDescription)}&location=${encodeURIComponent(eventLocation)}`;
      
      window.open(googleCalendarUrl, '_blank');
    });
  });
});
