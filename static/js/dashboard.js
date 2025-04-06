// Dashboard functionality for Women Entrepreneurs Hub
import { initializeApp } from 'https://www.gstatic.com/firebasejs/11.0.2/firebase-app.js';
import { getAuth } from 'https://www.gstatic.com/firebasejs/11.0.2/firebase-auth.js';
import { getFirestore, collection, query, where, getDocs, orderBy, limit } from 'https://www.gstatic.com/firebasejs/11.0.2/firebase-firestore.js';

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

// Dashboard data service
const dashboardService = {
  // Get recent sales
  getRecentSales: async (userId, limit = 5) => {
    try {
      if (!auth.currentUser) {
        throw new Error('User must be authenticated to view sales');
      }
      
      const ordersRef = collection(db, 'orders');
      const q = query(
        ordersRef,
        where('items', 'array-contains', { user_id: userId }),
        orderBy('created_at', 'desc'),
        limit(limit)
      );
      
      const querySnapshot = await getDocs(q);
      const orders = [];
      
      querySnapshot.forEach((doc) => {
        orders.push({
          id: doc.id,
          ...doc.data()
        });
      });
      
      return orders;
    } catch (error) {
      console.error('Error getting recent sales:', error);
      return [];
    }
  },
  
  // Get sales statistics
  getSalesStats: async (userId) => {
    try {
      if (!auth.currentUser) {
        throw new Error('User must be authenticated to view sales stats');
      }
      
      // Fetch sales data from backend API
      const response = await fetch(`/api/dashboard/sales-stats?user_id=${userId}`);
      const data = await response.json();
      
      return data;
    } catch (error) {
      console.error('Error getting sales stats:', error);
      return {
        total_sales: 0,
        total_products: 0,
        total_orders: 0,
        average_order_value: 0,
        monthly_sales: []
      };
    }
  },
  
  // Get recent products
  getRecentProducts: async (userId, limit = 5) => {
    try {
      if (!auth.currentUser) {
        throw new Error('User must be authenticated to view products');
      }
      
      const productsRef = collection(db, 'products');
      const q = query(
        productsRef,
        where('user_id', '==', userId),
        orderBy('created_at', 'desc'),
        limit(limit)
      );
      
      const querySnapshot = await getDocs(q);
      const products = [];
      
      querySnapshot.forEach((doc) => {
        products.push({
          id: doc.id,
          ...doc.data()
        });
      });
      
      return products;
    } catch (error) {
      console.error('Error getting recent products:', error);
      return [];
    }
  },
  
  // Get nearby businesses
  getNearbyBusinesses: async (lat, lng, radius = 10) => {
    try {
      // Fetch nearby businesses from backend API
      const response = await fetch(`/api/businesses/nearby?lat=${lat}&lng=${lng}&radius=${radius}`);
      const data = await response.json();
      
      return data;
    } catch (error) {
      console.error('Error getting nearby businesses:', error);
      return [];
    }
  },
  
  // Get upcoming events
  getUpcomingEvents: async (limit = 5) => {
    try {
      const eventsRef = collection(db, 'events');
      const q = query(
        eventsRef,
        where('start_datetime', '>=', new Date()),
        orderBy('start_datetime', 'asc'),
        limit(limit)
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
  }
};

// Initialize dashboard charts
function initCharts(userData) {
  if (!userData) return;
  
  // Load sales data for charts
  dashboardService.getSalesStats(userData.uid)
    .then(stats => {
      // Initialize sales trend chart
      const salesTrendCtx = document.getElementById('sales-trend-chart');
      if (salesTrendCtx) {
        const months = stats.monthly_sales.map(item => item.month);
        const salesData = stats.monthly_sales.map(item => item.amount);
        
        new Chart(salesTrendCtx, {
          type: 'line',
          data: {
            labels: months,
            datasets: [{
              label: 'Monthly Sales',
              data: salesData,
              borderColor: '#0d6efd',
              backgroundColor: 'rgba(13, 110, 253, 0.1)',
              tension: 0.3,
              fill: true
            }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: {
                position: 'top',
              },
              title: {
                display: true,
                text: 'Monthly Sales Trend'
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                ticks: {
                  callback: function(value) {
                    return '$' + value;
                  }
                }
              }
            }
          }
        });
      }
      
      // Initialize product categories chart
      const categoriesCtx = document.getElementById('categories-chart');
      if (categoriesCtx && stats.categories) {
        const categories = stats.categories.map(item => item.category);
        const categoryData = stats.categories.map(item => item.count);
        
        new Chart(categoriesCtx, {
          type: 'doughnut',
          data: {
            labels: categories,
            datasets: [{
              data: categoryData,
              backgroundColor: [
                '#0d6efd',
                '#6610f2',
                '#6f42c1',
                '#d63384',
                '#dc3545'
              ]
            }]
          },
          options: {
            responsive: true,
            plugins: {
              legend: {
                position: 'right',
              },
              title: {
                display: true,
                text: 'Product Categories'
              }
            }
          }
        });
      }
    })
    .catch(error => {
      console.error('Error initializing charts:', error);
    });
}

// Update dashboard UI with data
async function updateDashboardUI(userData) {
  if (!userData) return;
  
  try {
    // Load recent sales
    const recentSales = await dashboardService.getRecentSales(userData.uid);
    const salesContainer = document.getElementById('recent-sales');
    if (salesContainer) {
      if (recentSales.length === 0) {
        salesContainer.innerHTML = '<div class="text-center p-3">No recent sales</div>';
      } else {
        salesContainer.innerHTML = '';
        recentSales.forEach(sale => {
          const saleEl = document.createElement('div');
          saleEl.className = 'sale-item d-flex justify-content-between align-items-center p-2 border-bottom';
          
          const date = new Date(sale.created_at.seconds * 1000);
          const formattedDate = date.toLocaleDateString();
          
          saleEl.innerHTML = `
            <div class="sale-details">
              <div class="sale-id">Order #${sale.id.slice(0, 8)}</div>
              <div class="sale-date small text-muted">${formattedDate}</div>
            </div>
            <div class="sale-amount fw-bold">$${sale.total_amount.toFixed(2)}</div>
          `;
          
          salesContainer.appendChild(saleEl);
        });
      }
    }
    
    // Load sales stats
    const stats = await dashboardService.getSalesStats(userData.uid);
    
    // Update stats UI
    const totalSales = document.getElementById('total-sales');
    if (totalSales) {
      totalSales.textContent = `$${stats.total_sales.toFixed(2)}`;
    }
    
    const totalOrders = document.getElementById('total-orders');
    if (totalOrders) {
      totalOrders.textContent = stats.total_orders;
    }
    
    const totalProducts = document.getElementById('total-products');
    if (totalProducts) {
      totalProducts.textContent = stats.total_products;
    }
    
    const avgOrderValue = document.getElementById('avg-order-value');
    if (avgOrderValue) {
      avgOrderValue.textContent = `$${stats.average_order_value.toFixed(2)}`;
    }
    
    // Load recent products
    const recentProducts = await dashboardService.getRecentProducts(userData.uid);
    const productsContainer = document.getElementById('recent-products');
    if (productsContainer) {
      if (recentProducts.length === 0) {
        productsContainer.innerHTML = '<div class="text-center p-3">No products added yet</div>';
      } else {
        productsContainer.innerHTML = '';
        recentProducts.forEach(product => {
          const productEl = document.createElement('div');
          productEl.className = 'product-item d-flex align-items-center p-2 border-bottom';
          
          productEl.innerHTML = `
            <div class="product-image me-2">
              ${product.image_url ? `<img src="${product.image_url}" alt="${product.name}" width="40" height="40" class="rounded">` : 
              '<div class="bg-secondary rounded" style="width:40px;height:40px;"></div>'}
            </div>
            <div class="product-details flex-grow-1">
              <div class="product-name">${product.name}</div>
              <div class="product-price small">$${product.price.toFixed(2)}</div>
            </div>
            <div class="product-stock ${product.stock > 0 ? 'text-success' : 'text-danger'}">
              ${product.stock > 0 ? 'In Stock' : 'Out of Stock'}
            </div>
          `;
          
          productsContainer.appendChild(productEl);
        });
      }
    }
    
    // Load upcoming events
    const upcomingEvents = await dashboardService.getUpcomingEvents();
    const eventsContainer = document.getElementById('upcoming-events');
    if (eventsContainer) {
      if (upcomingEvents.length === 0) {
        eventsContainer.innerHTML = '<div class="text-center p-3">No upcoming events</div>';
      } else {
        eventsContainer.innerHTML = '';
        upcomingEvents.forEach(event => {
          const eventEl = document.createElement('div');
          eventEl.className = 'event-item p-2 border-bottom';
          
          const startDate = new Date(event.start_datetime.seconds * 1000);
          const formattedDate = startDate.toLocaleDateString();
          const formattedTime = startDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
          
          eventEl.innerHTML = `
            <div class="event-title fw-bold">${event.title}</div>
            <div class="event-time small text-muted">
              <i class="fa fa-calendar me-1"></i>${formattedDate} at ${formattedTime}
            </div>
            <div class="event-location small text-muted">
              ${event.is_virtual ? 
                `<i class="fa fa-video me-1"></i>Virtual Event` : 
                `<i class="fa fa-map-marker me-1"></i>${event.location}`}
            </div>
          `;
          
          eventsContainer.appendChild(eventEl);
        });
      }
    }
    
    // Initialize charts
    initCharts(userData);
    
    // Get user's location for nearby businesses
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(async (position) => {
        const { latitude, longitude } = position.coords;
        
        // Load nearby businesses
        const nearbyBusinesses = await dashboardService.getNearbyBusinesses(latitude, longitude);
        
        // Initialize map if available
        const mapContainer = document.getElementById('businesses-map');
        if (mapContainer && window.google && window.google.maps) {
          const map = new google.maps.Map(mapContainer, {
            center: { lat: latitude, lng: longitude },
            zoom: 12
          });
          
          // Add markers for each business
          nearbyBusinesses.forEach(business => {
            const marker = new google.maps.Marker({
              position: { lat: business.latitude, lng: business.longitude },
              map: map,
              title: business.name
            });
            
            const infoWindow = new google.maps.InfoWindow({
              content: `
                <div>
                  <h5>${business.name}</h5>
                  <p>${business.address}</p>
                  <p>${business.phone || ''}</p>
                </div>
              `
            });
            
            marker.addListener('click', () => {
              infoWindow.open(map, marker);
            });
          });
          
          // Add current location marker
          new google.maps.Marker({
            position: { lat: latitude, lng: longitude },
            map: map,
            title: 'Your Location',
            icon: {
              url: 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png'
            }
          });
        }
        
        // Update nearby businesses list
        const businessesList = document.getElementById('nearby-businesses');
        if (businessesList) {
          if (nearbyBusinesses.length === 0) {
            businessesList.innerHTML = '<div class="text-center p-3">No nearby businesses found</div>';
          } else {
            businessesList.innerHTML = '';
            nearbyBusinesses.forEach(business => {
              const businessEl = document.createElement('div');
              businessEl.className = 'business-item p-2 border-bottom';
              
              businessEl.innerHTML = `
                <div class="business-name fw-bold">${business.name}</div>
                <div class="business-address small text-muted">
                  <i class="fa fa-map-marker me-1"></i>${business.address}
                </div>
                ${business.phone ? `
                <div class="business-phone small text-muted">
                  <i class="fa fa-phone me-1"></i>${business.phone}
                </div>` : ''}
                ${business.distance ? `
                <div class="business-distance small text-muted">
                  <i class="fa fa-road me-1"></i>${business.distance.toFixed(1)} km away
                </div>` : ''}
              `;
              
              businessesList.appendChild(businessEl);
            });
          }
        }
      });
    }
  } catch (error) {
    console.error('Error updating dashboard UI:', error);
  }
}

// Initialize dashboard when document is loaded
document.addEventListener('DOMContentLoaded', () => {
  // Check if user is authenticated
  auth.onAuthStateChanged(user => {
    if (user) {
      // Update dashboard with user data
      updateDashboardUI(user);
    } else {
      // Redirect to login page
      window.location.href = '/login';
    }
  });
});
