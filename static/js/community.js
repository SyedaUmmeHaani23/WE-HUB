// Community functionality for Women Entrepreneurs Hub
import { initializeApp } from 'https://www.gstatic.com/firebasejs/11.0.2/firebase-app.js';
import { getAuth } from 'https://www.gstatic.com/firebasejs/11.0.2/firebase-auth.js';
import { getFirestore, collection, addDoc, updateDoc, deleteDoc, doc, getDoc, getDocs, query, where, orderBy } from 'https://www.gstatic.com/firebasejs/11.0.2/firebase-firestore.js';
import { getStorage, ref, uploadBytes, getDownloadURL } from 'https://www.gstatic.com/firebasejs/11.0.2/firebase-storage.js';

// Firebase configuration will be injected from the server
let firebaseConfig = {};
try {
  firebaseConfig = {
    apiKey: document.getElementById('firebase-config').getAttribute('data-api-key'),
    projectId: document.getElementById('firebase-config').getAttribute('data-project-id'),
    appId: document.getElementById('firebase-config').getAttribute('data-app-id'),
    authDomain: `${document.getElementById('firebase-config').getAttribute('data-project-id')}.firebaseapp.com`,
    storageBucket: `${document.getElementById('firebase-config').getAttribute('data-project-id')}.appspot.com`,
  };
} catch (error) {
  console.error('Error loading Firebase config:', error);
}

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const storage = getStorage(app);

// Forum service for community posts and comments
const forumService = {
  // Get all forum posts
  getAllPosts: async () => {
    try {
      const postsRef = collection(db, 'forum_posts');
      const q = query(postsRef, orderBy('created_at', 'desc'));
      const querySnapshot = await getDocs(q);
      const posts = [];
      
      querySnapshot.forEach((doc) => {
        posts.push({
          id: doc.id,
          ...doc.data()
        });
      });
      
      return posts;
    } catch (error) {
      console.error('Error getting forum posts:', error);
      return [];
    }
  },
  
  // Get posts by category
  getPostsByCategory: async (category) => {
    try {
      const postsRef = collection(db, 'forum_posts');
      const q = query(postsRef, where('category', '==', category), orderBy('created_at', 'desc'));
      const querySnapshot = await getDocs(q);
      const posts = [];
      
      querySnapshot.forEach((doc) => {
        posts.push({
          id: doc.id,
          ...doc.data()
        });
      });
      
      return posts;
    } catch (error) {
      console.error('Error getting posts by category:', error);
      return [];
    }
  },
  
  // Get post by ID
  getPost: async (postId) => {
    try {
      const postRef = doc(db, 'forum_posts', postId);
      const postSnap = await getDoc(postRef);
      
      if (postSnap.exists()) {
        return {
          id: postSnap.id,
          ...postSnap.data()
        };
      } else {
        console.error('Post not found');
        return null;
      }
    } catch (error) {
      console.error('Error getting post:', error);
      return null;
    }
  },
  
  // Get comments for a post
  getComments: async (postId) => {
    try {
      const commentsRef = collection(db, 'forum_comments');
      const q = query(commentsRef, where('post_id', '==', postId), orderBy('created_at', 'asc'));
      const querySnapshot = await getDocs(q);
      const comments = [];
      
      querySnapshot.forEach((doc) => {
        comments.push({
          id: doc.id,
          ...doc.data()
        });
      });
      
      return comments;
    } catch (error) {
      console.error('Error getting comments:', error);
      return [];
    }
  },
  
  // Create a new post
  createPost: async (postData) => {
    try {
      if (!auth.currentUser) {
        throw new Error('User must be authenticated to create a post');
      }
      
      // Add post to Firestore
      const newPost = {
        ...postData,
        user_id: auth.currentUser.uid,
        user_name: auth.currentUser.displayName || 'Anonymous',
        user_photo: auth.currentUser.photoURL || null,
        created_at: new Date(),
        updated_at: new Date()
      };
      
      const docRef = await addDoc(collection(db, 'forum_posts'), newPost);
      
      // Send to backend to sync
      await fetch('/api/forum/posts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...newPost,
          firebase_id: docRef.id
        }),
      });
      
      return docRef.id;
    } catch (error) {
      console.error('Error creating post:', error);
      throw error;
    }
  },
  
  // Update a post
  updatePost: async (postId, postData) => {
    try {
      if (!auth.currentUser) {
        throw new Error('User must be authenticated to update a post');
      }
      
      // Check if user is the author
      const post = await this.getPost(postId);
      if (post.user_id !== auth.currentUser.uid) {
        throw new Error('You can only edit your own posts');
      }
      
      // Update post in Firestore
      const postRef = doc(db, 'forum_posts', postId);
      
      const updatedPost = {
        ...postData,
        updated_at: new Date()
      };
      
      await updateDoc(postRef, updatedPost);
      
      // Send to backend to sync
      await fetch(`/api/forum/posts/${postId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedPost),
      });
      
      return postId;
    } catch (error) {
      console.error('Error updating post:', error);
      throw error;
    }
  },
  
  // Delete a post
  deletePost: async (postId) => {
    try {
      if (!auth.currentUser) {
        throw new Error('User must be authenticated to delete a post');
      }
      
      // Check if user is the author
      const post = await this.getPost(postId);
      if (post.user_id !== auth.currentUser.uid) {
        throw new Error('You can only delete your own posts');
      }
      
      // Delete post from Firestore
      const postRef = doc(db, 'forum_posts', postId);
      await deleteDoc(postRef);
      
      // Send to backend to sync
      await fetch(`/api/forum/posts/${postId}`, {
        method: 'DELETE'
      });
      
      return true;
    } catch (error) {
      console.error('Error deleting post:', error);
      throw error;
    }
  },
  
  // Add a comment to a post
  addComment: async (postId, commentData) => {
    try {
      if (!auth.currentUser) {
        throw new Error('User must be authenticated to add a comment');
      }
      
      // Add comment to Firestore
      const newComment = {
        post_id: postId,
        ...commentData,
        user_id: auth.currentUser.uid,
        user_name: auth.currentUser.displayName || 'Anonymous',
        user_photo: auth.currentUser.photoURL || null,
        created_at: new Date(),
        updated_at: new Date()
      };
      
      const docRef = await addDoc(collection(db, 'forum_comments'), newComment);
      
      // Send to backend to sync
      await fetch('/api/forum/comments', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...newComment,
          firebase_id: docRef.id
        }),
      });
      
      return docRef.id;
    } catch (error) {
      console.error('Error adding comment:', error);
      throw error;
    }
  }
};

// Event service for community events and workshops
const eventService = {
  // Get all events
  getAllEvents: async () => {
    try {
      const eventsRef = collection(db, 'events');
      const q = query(eventsRef, orderBy('start_datetime', 'asc'));
      const querySnapshot = await getDocs(q);
      const events = [];
      
      querySnapshot.forEach((doc) => {
        events.push({
          id: doc.id,
          ...doc.data()
        });
      });
      
      return events;
    } catch (error) {
      console.error('Error getting events:', error);
      return [];
    }
  },
  
  // Get upcoming events
  getUpcomingEvents: async () => {
    try {
      const eventsRef = collection(db, 'events');
      const q = query(
        eventsRef,
        where('start_datetime', '>=', new Date()),
        orderBy('start_datetime', 'asc')
      );
      const querySnapshot = await getDocs(q);
      const events = [];
      
      querySnapshot.forEach((doc) => {
        events.push({
          id: doc.id,
          ...doc.data()
        });
      });
      
      return events;
    } catch (error) {
      console.error('Error getting upcoming events:', error);
      return [];
    }
  },
  
  // Get past events
  getPastEvents: async () => {
    try {
      const eventsRef = collection(db, 'events');
      const q = query(
        eventsRef,
        where('end_datetime', '<', new Date()),
        orderBy('end_datetime', 'desc')
      );
      const querySnapshot = await getDocs(q);
      const events = [];
      
      querySnapshot.forEach((doc) => {
        events.push({
          id: doc.id,
          ...doc.data()
        });
      });
      
      return events;
    } catch (error) {
      console.error('Error getting past events:', error);
      return [];
    }
  },
  
  // Get event by ID
  getEvent: async (eventId) => {
    try {
      const eventRef = doc(db, 'events', eventId);
      const eventSnap = await getDoc(eventRef);
      
      if (eventSnap.exists()) {
        return {
          id: eventSnap.id,
          ...eventSnap.data()
        };
      } else {
        console.error('Event not found');
        return null;
      }
    } catch (error) {
      console.error('Error getting event:', error);
      return null;
    }
  },
  
  // Create a new event
  createEvent: async (eventData, imageFile) => {
    try {
      if (!auth.currentUser) {
        throw new Error('User must be authenticated to create an event');
      }
      
      // Upload image if provided
      let imageUrl = null;
      if (imageFile) {
        const storageRef = ref(storage, `event_images/${auth.currentUser.uid}/${Date.now()}_${imageFile.name}`);
        await uploadBytes(storageRef, imageFile);
        imageUrl = await getDownloadURL(storageRef);
      }
      
      // Add event to Firestore
      const newEvent = {
        ...eventData,
        image_url: imageUrl,
        user_id: auth.currentUser.uid,
        created_at: new Date(),
        updated_at: new Date()
      };
      
      // Convert string dates to Date objects
      if (typeof newEvent.start_datetime === 'string') {
        newEvent.start_datetime = new Date(newEvent.start_datetime);
      }
      
      if (typeof newEvent.end_datetime === 'string') {
        newEvent.end_datetime = new Date(newEvent.end_datetime);
      }
      
      const docRef = await addDoc(collection(db, 'events'), newEvent);
      
      // Send to backend to sync
      await fetch('/api/events', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...newEvent,
          firebase_id: docRef.id
        }),
      });
      
      return docRef.id;
    } catch (error) {
      console.error('Error creating event:', error);
      throw error;
    }
  },
  
  // Register for an event
  registerForEvent: async (eventId) => {
    try {
      if (!auth.currentUser) {
        throw new Error('User must be authenticated to register for an event');
      }
      
      // Check if already registered
      const registrationsRef = collection(db, 'event_registrations');
      const q = query(
        registrationsRef,
        where('event_id', '==', eventId),
        where('user_id', '==', auth.currentUser.uid)
      );
      
      const querySnapshot = await getDocs(q);
      if (!querySnapshot.empty) {
        throw new Error('You are already registered for this event');
      }
      
      // Create registration
      const registration = {
        event_id: eventId,
        user_id: auth.currentUser.uid,
        registration_date: new Date(),
        status: 'registered'
      };
      
      const docRef = await addDoc(collection(db, 'event_registrations'), registration);
      
      // Send to backend to sync
      await fetch('/api/events/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...registration,
          firebase_id: docRef.id
        }),
      });
      
      return docRef.id;
    } catch (error) {
      console.error('Error registering for event:', error);
      throw error;
    }
  },
  
  // Check if user is registered for an event
  isUserRegistered: async (eventId) => {
    try {
      if (!auth.currentUser) {
        return false;
      }
      
      const registrationsRef = collection(db, 'event_registrations');
      const q = query(
        registrationsRef,
        where('event_id', '==', eventId),
        where('user_id', '==', auth.currentUser.uid)
      );
      
      const querySnapshot = await getDocs(q);
      return !querySnapshot.empty;
    } catch (error) {
      console.error('Error checking registration:', error);
      return false;
    }
  }
};

// Initialize community functionality when document is loaded
document.addEventListener('DOMContentLoaded', () => {
  // Handle forum post form submission
  const forumForm = document.getElementById('forum-post-form');
  if (forumForm) {
    forumForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      if (!auth.currentUser) {
        alert('Please sign in to create a post');
        return;
      }
      
      const formData = new FormData(forumForm);
      const postData = {
        title: formData.get('title'),
        content: formData.get('content'),
        category: formData.get('category')
      };
      
      try {
        await forumService.createPost(postData);
        alert('Post created successfully!');
        forumForm.reset();
        
        // Reload posts
        loadForumPosts();
      } catch (error) {
        alert(`Error: ${error.message}`);
      }
    });
  }
  
  // Handle event form submission
  const eventForm = document.getElementById('event-form');
  if (eventForm) {
    eventForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      if (!auth.currentUser) {
        alert('Please sign in to create an event');
        return;
      }
      
      const formData = new FormData(eventForm);
      const eventData = {
        title: formData.get('title'),
        description: formData.get('description'),
        start_datetime: new Date(formData.get('start_date') + 'T' + formData.get('start_time')),
        end_datetime: new Date(formData.get('end_date') + 'T' + formData.get('end_time')),
        location: formData.get('location'),
        is_virtual: formData.get('is_virtual') === 'on',
        virtual_link: formData.get('virtual_link'),
        max_participants: parseInt(formData.get('max_participants') || '0')
      };
      
      const imageFile = formData.get('image');
      
      try {
        await eventService.createEvent(eventData, imageFile.size > 0 ? imageFile : null);
        alert('Event created successfully!');
        eventForm.reset();
        
        // Reload events
        loadEvents();
      } catch (error) {
        alert(`Error: ${error.message}`);
      }
    });
  }
  
  // Handle event registration
  document.addEventListener('click', async (e) => {
    if (e.target.matches('.register-event-btn')) {
      e.preventDefault();
      
      if (!auth.currentUser) {
        alert('Please sign in to register for events');
        return;
      }
      
      const eventId = e.target.getAttribute('data-event-id');
      
      try {
        await eventService.registerForEvent(eventId);
        alert('You have successfully registered for this event!');
        
        // Update button to show registered
        e.target.textContent = 'Registered';
        e.target.disabled = true;
        e.target.classList.remove('btn-primary');
        e.target.classList.add('btn-success');
      } catch (error) {
        alert(`Error: ${error.message}`);
      }
    }
  });
  
  // Handle comment form submission
  document.addEventListener('submit', async (e) => {
    if (e.target.matches('.comment-form')) {
      e.preventDefault();
      
      if (!auth.currentUser) {
        alert('Please sign in to add a comment');
        return;
      }
      
      const postId = e.target.getAttribute('data-post-id');
      const commentContent = e.target.querySelector('.comment-content').value;
      
      try {
        await forumService.addComment(postId, {
          content: commentContent
        });
        
        // Clear the comment input
        e.target.querySelector('.comment-content').value = '';
        
        // Reload comments
        loadComments(postId);
      } catch (error) {
        alert(`Error: ${error.message}`);
      }
    }
  });
  
  // Load forum posts if on the forum page
  const forumPostsContainer = document.getElementById('forum-posts');
  if (forumPostsContainer) {
    loadForumPosts();
  }
  
  // Load events if on the events page
  const eventsContainer = document.getElementById('upcoming-events-list');
  if (eventsContainer) {
    loadEvents();
  }
});

// Load forum posts
async function loadForumPosts() {
  const forumPostsContainer = document.getElementById('forum-posts');
  if (!forumPostsContainer) return;
  
  try {
    const categoryFilter = document.getElementById('category-filter');
    let posts;
    
    if (categoryFilter && categoryFilter.value && categoryFilter.value !== 'all') {
      posts = await forumService.getPostsByCategory(categoryFilter.value);
    } else {
      posts = await forumService.getAllPosts();
    }
    
    if (posts.length === 0) {
      forumPostsContainer.innerHTML = '<div class="text-center p-4">No posts found. Be the first to start a discussion!</div>';
    } else {
      forumPostsContainer.innerHTML = '';
      
      posts.forEach(post => {
        const postEl = document.createElement('div');
        postEl.className = 'card mb-3';
        
        const postDate = new Date(post.created_at.seconds * 1000);
        const formattedDate = postDate.toLocaleDateString() + ' ' + postDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        postEl.innerHTML = `
          <div class="card-header d-flex justify-content-between align-items-center">
            <div class="d-flex align-items-center">
              ${post.user_photo ? 
                `<img src="${post.user_photo}" alt="${post.user_name}" class="rounded-circle me-2" width="30" height="30">` : 
                '<div class="bg-secondary rounded-circle me-2" style="width:30px;height:30px;"></div>'}
              <span class="fw-bold">${post.user_name}</span>
            </div>
            <small class="text-muted">${formattedDate}</small>
          </div>
          <div class="card-body">
            <h5 class="card-title">${post.title}</h5>
            <p class="card-text">${post.content}</p>
            ${post.category ? `<span class="badge bg-secondary">${post.category}</span>` : ''}
            <hr>
            <div class="d-flex justify-content-between">
              <button class="btn btn-sm btn-outline-primary view-comments-btn" data-post-id="${post.id}">
                View Comments
              </button>
              <button class="btn btn-sm btn-outline-secondary add-comment-btn" data-post-id="${post.id}">
                Add Comment
              </button>
            </div>
            <div class="comments-container mt-3" id="comments-${post.id}" style="display:none;"></div>
            <form class="comment-form mt-3" data-post-id="${post.id}" style="display:none;">
              <div class="form-group">
                <textarea class="form-control comment-content" rows="2" placeholder="Write a comment..." required></textarea>
              </div>
              <button type="submit" class="btn btn-sm btn-primary mt-2">Submit Comment</button>
            </form>
          </div>
        `;
        
        forumPostsContainer.appendChild(postEl);
        
        // Add event listeners for comments
        const viewCommentsBtn = postEl.querySelector('.view-comments-btn');
        const addCommentBtn = postEl.querySelector('.add-comment-btn');
        const commentsContainer = postEl.querySelector('.comments-container');
        const commentForm = postEl.querySelector('.comment-form');
        
        viewCommentsBtn.addEventListener('click', () => {
          if (commentsContainer.style.display === 'none') {
            loadComments(post.id);
            commentsContainer.style.display = 'block';
            viewCommentsBtn.textContent = 'Hide Comments';
          } else {
            commentsContainer.style.display = 'none';
            viewCommentsBtn.textContent = 'View Comments';
          }
        });
        
        addCommentBtn.addEventListener('click', () => {
          if (commentForm.style.display === 'none') {
            commentForm.style.display = 'block';
            addCommentBtn.textContent = 'Cancel';
          } else {
            commentForm.style.display = 'none';
            addCommentBtn.textContent = 'Add Comment';
          }
        });
      });
    }
  } catch (error) {
    console.error('Error loading forum posts:', error);
    forumPostsContainer.innerHTML = `<div class="alert alert-danger">Error loading forum posts: ${error.message}</div>`;
  }
}

// Load comments for a post
async function loadComments(postId) {
  const commentsContainer = document.getElementById(`comments-${postId}`);
  if (!commentsContainer) return;
  
  try {
    commentsContainer.innerHTML = '<div class="text-center"><div class="spinner-border spinner-border-sm" role="status"></div> Loading comments...</div>';
    
    const comments = await forumService.getComments(postId);
    
    if (comments.length === 0) {
      commentsContainer.innerHTML = '<div class="text-center p-2">No comments yet. Be the first to comment!</div>';
    } else {
      commentsContainer.innerHTML = '';
      
      comments.forEach(comment => {
        const commentEl = document.createElement('div');
        commentEl.className = 'comment p-2 border-top';
        
        const commentDate = new Date(comment.created_at.seconds * 1000);
        const formattedDate = commentDate.toLocaleDateString() + ' ' + commentDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        commentEl.innerHTML = `
          <div class="d-flex justify-content-between align-items-center">
            <div class="d-flex align-items-center">
              ${comment.user_photo ? 
                `<img src="${comment.user_photo}" alt="${comment.user_name}" class="rounded-circle me-2" width="24" height="24">` : 
                '<div class="bg-secondary rounded-circle me-2" style="width:24px;height:24px;"></div>'}
              <span class="fw-bold small">${comment.user_name}</span>
            </div>
            <small class="text-muted">${formattedDate}</small>
          </div>
          <div class="comment-content mt-1">${comment.content}</div>
        `;
        
        commentsContainer.appendChild(commentEl);
      });
    }
  } catch (error) {
    console.error('Error loading comments:', error);
    commentsContainer.innerHTML = `<div class="alert alert-danger">Error loading comments: ${error.message}</div>`;
  }
}

// Load events
async function loadEvents() {
  const upcomingEventsContainer = document.getElementById('upcoming-events-list');
  const pastEventsContainer = document.getElementById('past-events-list');
  
  if (!upcomingEventsContainer && !pastEventsContainer) return;
  
  try {
    if (upcomingEventsContainer) {
      upcomingEventsContainer.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div> Loading upcoming events...</div>';
      
      const upcomingEvents = await eventService.getUpcomingEvents();
      
      if (upcomingEvents.length === 0) {
        upcomingEventsContainer.innerHTML = '<div class="text-center p-4">No upcoming events scheduled.</div>';
      } else {
        upcomingEventsContainer.innerHTML = '';
        
        upcomingEvents.forEach(async event => {
          const eventEl = document.createElement('div');
          eventEl.className = 'card mb-3';
          
          const startDate = new Date(event.start_datetime.seconds * 1000);
          const endDate = new Date(event.end_datetime.seconds * 1000);
          
          const formattedStartDate = startDate.toLocaleDateString();
          const formattedStartTime = startDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
          const formattedEndTime = endDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
          
          // Check if user is registered
          const isRegistered = await eventService.isUserRegistered(event.id);
          
          eventEl.innerHTML = `
            <div class="row g-0">
              ${event.image_url ? `
              <div class="col-md-4">
                <img src="${event.image_url}" class="img-fluid rounded-start" alt="${event.title}">
              </div>
              <div class="col-md-8">
              ` : `<div class="col-12">`}
                <div class="card-body">
                  <h5 class="card-title">${event.title}</h5>
                  <p class="card-text">${event.description}</p>
                  <div class="event-details mb-3">
                    <div><i class="fa fa-calendar me-2"></i>${formattedStartDate}</div>
                    <div><i class="fa fa-clock-o me-2"></i>${formattedStartTime} - ${formattedEndTime}</div>
                    <div>
                      ${event.is_virtual ? 
                        `<i class="fa fa-video-camera me-2"></i>Virtual Event` : 
                        `<i class="fa fa-map-marker me-2"></i>${event.location}`}
                    </div>
                    ${event.max_participants ? `
                    <div><i class="fa fa-users me-2"></i>Max Participants: ${event.max_participants}</div>
                    ` : ''}
                  </div>
                  
                  <button class="btn ${isRegistered ? 'btn-success' : 'btn-primary'} register-event-btn" 
                    data-event-id="${event.id}" ${isRegistered ? 'disabled' : ''}>
                    ${isRegistered ? 'Registered' : 'Register Now'}
                  </button>
                  
                  ${event.is_virtual && event.virtual_link && isRegistered ? `
                  <a href="${event.virtual_link}" target="_blank" class="btn btn-outline-primary ms-2">
                    Join Virtual Event
                  </a>
                  ` : ''}
                </div>
              </div>
            </div>
          `;
          
          upcomingEventsContainer.appendChild(eventEl);
        });
      }
    }
    
    if (pastEventsContainer) {
      pastEventsContainer.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div> Loading past events...</div>';
      
      const pastEvents = await eventService.getPastEvents();
      
      if (pastEvents.length === 0) {
        pastEventsContainer.innerHTML = '<div class="text-center p-4">No past events found.</div>';
      } else {
        pastEventsContainer.innerHTML = '';
        
        pastEvents.forEach(event => {
          const eventEl = document.createElement('div');
          eventEl.className = 'card mb-3';
          
          const startDate = new Date(event.start_datetime.seconds * 1000);
          const formattedStartDate = startDate.toLocaleDateString();
          
          eventEl.innerHTML = `
            <div class="row g-0">
              ${event.image_url ? `
              <div class="col-md-4">
                <img src="${event.image_url}" class="img-fluid rounded-start" alt="${event.title}">
              </div>
              <div class="col-md-8">
              ` : `<div class="col-12">`}
                <div class="card-body">
                  <h5 class="card-title">${event.title}</h5>
                  <p class="card-text">${event.description}</p>
                  <div class="event-details mb-3">
                    <div><i class="fa fa-calendar me-2"></i>${formattedStartDate}</div>
                    <div>
                      ${event.is_virtual ? 
                        `<i class="fa fa-video-camera me-2"></i>Virtual Event` : 
                        `<i class="fa fa-map-marker me-2"></i>${event.location}`}
                    </div>
                  </div>
                  <div class="badge bg-secondary">Past Event</div>
                </div>
              </div>
            </div>
          `;
          
          pastEventsContainer.appendChild(eventEl);
        });
      }
    }
  } catch (error) {
    console.error('Error loading events:', error);
    if (upcomingEventsContainer) {
      upcomingEventsContainer.innerHTML = `<div class="alert alert-danger">Error loading upcoming events: ${error.message}</div>`;
    }
    if (pastEventsContainer) {
      pastEventsContainer.innerHTML = `<div class="alert alert-danger">Error loading past events: ${error.message}</div>`;
    }
  }
}

// Export services
window.forumService = forumService;
window.eventService = eventService;
