document.addEventListener('DOMContentLoaded', function() {
  // Render analytics chart if element exists
  const salesChartElement = document.getElementById('sales-chart');
  if (salesChartElement) {
    // Get data from the element's data attributes
    const dates = salesChartElement.dataset.dates.split(',');
    const views = salesChartElement.dataset.views.split(',').map(Number);
    
    // Create the chart
    const ctx = salesChartElement.getContext('2d');
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: dates,
        datasets: [{
          label: 'Daily Views',
          data: views,
          backgroundColor: 'rgba(54, 162, 235, 0.2)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 2,
          tension: 0.3,
          pointBackgroundColor: 'rgba(54, 162, 235, 1)',
          pointRadius: 3
        }]
      },
      options: {
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              precision: 0
            }
          }
        },
        plugins: {
          title: {
            display: true,
            text: 'Daily Views (Last 7 Days)',
            font: {
              size: 16
            }
          },
          legend: {
            display: false
          }
        },
        responsive: true,
        maintainAspectRatio: false
      }
    });
  }
  
  // Render category distribution chart if element exists
  const categoryChartElement = document.getElementById('category-chart');
  if (categoryChartElement && categoryChartElement.dataset.categories) {
    const categories = JSON.parse(categoryChartElement.dataset.categories);
    const categoryLabels = Object.keys(categories);
    const categoryData = Object.values(categories);
    
    // Create a color array
    const colors = [
      'rgba(54, 162, 235, 0.7)',
      'rgba(255, 99, 132, 0.7)',
      'rgba(255, 206, 86, 0.7)',
      'rgba(75, 192, 192, 0.7)',
      'rgba(153, 102, 255, 0.7)',
      'rgba(255, 159, 64, 0.7)',
      'rgba(199, 199, 199, 0.7)'
    ];
    
    // Create the chart
    const ctx = categoryChartElement.getContext('2d');
    new Chart(ctx, {
      type: 'pie',
      data: {
        labels: categoryLabels,
        datasets: [{
          data: categoryData,
          backgroundColor: colors.slice(0, categoryLabels.length),
          borderWidth: 1
        }]
      },
      options: {
        plugins: {
          title: {
            display: true,
            text: 'Products by Category',
            font: {
              size: 16
            }
          }
        },
        responsive: true,
        maintainAspectRatio: false
      }
    });
  }
  
  // Fetch and render 30-day chart if element exists
  const thirtyDayChartElement = document.getElementById('thirty-day-chart');
  if (thirtyDayChartElement) {
    fetch('/dashboard/api/analytics')
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          const dates = data.data.dates;
          const views = data.data.views;
          
          // Create the chart
          const ctx = thirtyDayChartElement.getContext('2d');
          new Chart(ctx, {
            type: 'line',
            data: {
              labels: dates,
              datasets: [{
                label: 'Daily Views',
                data: views,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 2,
                tension: 0.3,
                pointBackgroundColor: 'rgba(75, 192, 192, 1)',
                pointRadius: 3
              }]
            },
            options: {
              scales: {
                y: {
                  beginAtZero: true,
                  ticks: {
                    precision: 0
                  }
                },
                x: {
                  ticks: {
                    maxTicksLimit: 10
                  }
                }
              },
              plugins: {
                title: {
                  display: true,
                  text: 'Daily Views (Last 30 Days)',
                  font: {
                    size: 16
                  }
                }
              },
              responsive: true,
              maintainAspectRatio: false
            }
          });
        }
      })
      .catch(error => {
        console.error('Error fetching analytics data:', error);
        thirtyDayChartElement.innerHTML = '<div class="alert alert-danger">Error loading analytics data</div>';
      });
  }
  
  // Initialize Google Maps for nearby businesses if element exists
  const mapElement = document.getElementById('business-map');
  if (mapElement && typeof google !== 'undefined') {
    // Get business locations from the data attribute
    const businesses = JSON.parse(mapElement.dataset.businesses || '[]');
    
    // Initialize the map
    const map = new google.maps.Map(mapElement, {
      center: { lat: 37.7749, lng: -122.4194 }, // Default to San Francisco
      zoom: 12,
      styles: [
        {
          "featureType": "administrative",
          "elementType": "labels.text.fill",
          "stylers": [{"color": "#444444"}]
        },
        {
          "featureType": "landscape",
          "elementType": "all",
          "stylers": [{"color": "#f2f2f2"}]
        },
        {
          "featureType": "poi",
          "elementType": "all",
          "stylers": [{"visibility": "off"}]
        },
        {
          "featureType": "road",
          "elementType": "all",
          "stylers": [{"saturation": -100}, {"lightness": 45}]
        },
        {
          "featureType": "road.highway",
          "elementType": "all",
          "stylers": [{"visibility": "simplified"}]
        },
        {
          "featureType": "road.arterial",
          "elementType": "labels.icon",
          "stylers": [{"visibility": "off"}]
        },
        {
          "featureType": "transit",
          "elementType": "all",
          "stylers": [{"visibility": "off"}]
        },
        {
          "featureType": "water",
          "elementType": "all",
          "stylers": [{"color": "#c4c4c4"}, {"visibility": "on"}]
        }
      ]
    });
    
    // Add markers for each business
    const bounds = new google.maps.LatLngBounds();
    const infoWindow = new google.maps.InfoWindow();
    
    businesses.forEach(business => {
      // For demonstration purposes, generate random coordinates around San Francisco
      // In a real implementation, this would use actual business coordinates
      const lat = 37.7749 + (Math.random() - 0.5) * 0.05;
      const lng = -122.4194 + (Math.random() - 0.5) * 0.05;
      const position = { lat, lng };
      
      // Create marker
      const marker = new google.maps.Marker({
        position,
        map,
        title: business.name,
        icon: {
          url: 'https://maps.google.com/mapfiles/ms/icons/pink-dot.png'
        }
      });
      
      // Create info window content
      const content = `
        <div class="map-info-window">
          <h5>${business.name}</h5>
          <p>${business.category || 'Various Categories'}</p>
          <p>${business.location || 'Location not specified'}</p>
          <a href="/profiles/${business.id}" class="btn btn-sm btn-primary">View Profile</a>
        </div>
      `;
      
      // Add click event to marker
      marker.addListener('click', () => {
        infoWindow.setContent(content);
        infoWindow.open(map, marker);
      });
      
      // Extend bounds
      bounds.extend(position);
    });
    
    // Fit map to bounds if there are businesses
    if (businesses.length > 0) {
      map.fitBounds(bounds);
    }
  }
});
