// Google Maps integration for Women Entrepreneurs Hub
document.addEventListener('DOMContentLoaded', () => {
  // Initialize maps if Google Maps API is loaded and map container exists
  if (window.google && window.google.maps) {
    initMaps();
  } else {
    // Google Maps API not loaded yet, wait for it
    window.initMaps = initMaps;
  }
});

// Initialize all maps on the page
function initMaps() {
  // Initialize business map
  const businessMapContainer = document.getElementById('business-map');
  if (businessMapContainer) {
    initBusinessMap(businessMapContainer);
  }
  
  // Initialize nearby businesses map
  const nearbyBusinessesMap = document.getElementById('nearby-businesses-map');
  if (nearbyBusinessesMap) {
    initNearbyBusinessesMap(nearbyBusinessesMap);
  }
  
  // Initialize event location map
  const eventLocationMap = document.getElementById('event-location-map');
  if (eventLocationMap) {
    const lat = parseFloat(eventLocationMap.getAttribute('data-lat'));
    const lng = parseFloat(eventLocationMap.getAttribute('data-lng'));
    const location = eventLocationMap.getAttribute('data-location');
    
    if (lat && lng) {
      initEventMap(eventLocationMap, lat, lng, location);
    }
  }
}

// Initialize map for a business profile
function initBusinessMap(mapContainer) {
  // Get business location from data attributes
  const lat = parseFloat(mapContainer.getAttribute('data-lat'));
  const lng = parseFloat(mapContainer.getAttribute('data-lng'));
  const name = mapContainer.getAttribute('data-name');
  
  // If no coordinates, show a default location (center of US)
  const center = (lat && lng) ? { lat, lng } : { lat: 37.0902, lng: -95.7129 };
  
  // Create the map
  const map = new google.maps.Map(mapContainer, {
    center: center,
    zoom: (lat && lng) ? 15 : 4,
    styles: mapStyles // Custom map styles defined below
  });
  
  // If coordinates are available, add a marker
  if (lat && lng) {
    const marker = new google.maps.Marker({
      position: { lat, lng },
      map: map,
      title: name || 'Business Location'
    });
    
    // Add info window if name is available
    if (name) {
      const infoWindow = new google.maps.InfoWindow({
        content: `<div><strong>${name}</strong></div>`
      });
      
      marker.addListener('click', () => {
        infoWindow.open(map, marker);
      });
    }
  }
}

// Initialize map for nearby businesses
function initNearbyBusinessesMap(mapContainer) {
  // Start with a default location (user's location will be determined)
  const defaultCenter = { lat: 37.0902, lng: -95.7129 };
  
  // Create the map
  const map = new google.maps.Map(mapContainer, {
    center: defaultCenter,
    zoom: 12,
    styles: mapStyles // Custom map styles defined below
  });
  
  // Try to get user's location
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      // Success callback
      (position) => {
        const userLocation = {
          lat: position.coords.latitude,
          lng: position.coords.longitude
        };
        
        // Center map on user's location
        map.setCenter(userLocation);
        
        // Add marker for user's location
        new google.maps.Marker({
          position: userLocation,
          map: map,
          title: 'Your Location',
          icon: {
            url: 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png'
          }
        });
        
        // Fetch nearby businesses
        fetchNearbyBusinesses(userLocation.lat, userLocation.lng, map);
      },
      // Error callback
      (error) => {
        console.error('Error getting location:', error);
        // If can't get location, just load businesses from a default location
        fetchNearbyBusinesses(defaultCenter.lat, defaultCenter.lng, map);
      }
    );
  } else {
    console.error('Geolocation not supported by this browser');
    // If geolocation not supported, just load businesses from a default location
    fetchNearbyBusinesses(defaultCenter.lat, defaultCenter.lng, map);
  }
}

// Fetch nearby women-owned businesses and add them to the map
async function fetchNearbyBusinesses(lat, lng, map) {
  try {
    // Fetch nearby businesses from backend API
    const response = await fetch(`/api/businesses/nearby?lat=${lat}&lng=${lng}&radius=10`);
    const businesses = await response.json();
    
    // Add markers for each business
    businesses.forEach(business => {
      if (business.latitude && business.longitude) {
        const marker = new google.maps.Marker({
          position: { lat: business.latitude, lng: business.longitude },
          map: map,
          title: business.name || 'Business'
        });
        
        // Create info window with business details
        const infoWindow = new google.maps.InfoWindow({
          content: `
            <div>
              <h5>${business.name}</h5>
              <p>${business.address || ''}</p>
              ${business.phone ? `<p>Phone: ${business.phone}</p>` : ''}
              ${business.website ? `<p><a href="${business.website}" target="_blank">Visit Website</a></p>` : ''}
              ${business.distance ? `<p>Distance: ${business.distance.toFixed(1)} km</p>` : ''}
            </div>
          `
        });
        
        // Show info window when marker is clicked
        marker.addListener('click', () => {
          infoWindow.open(map, marker);
        });
      }
    });
    
    // If no businesses found, zoom out
    if (businesses.length === 0) {
      map.setZoom(10);
    }
  } catch (error) {
    console.error('Error fetching nearby businesses:', error);
  }
}

// Initialize map for event location
function initEventMap(mapContainer, lat, lng, locationName) {
  // Create the map
  const map = new google.maps.Map(mapContainer, {
    center: { lat, lng },
    zoom: 15,
    styles: mapStyles // Custom map styles defined below
  });
  
  // Add marker for event location
  const marker = new google.maps.Marker({
    position: { lat, lng },
    map: map,
    title: locationName || 'Event Location'
  });
  
  // Add info window with location name
  if (locationName) {
    const infoWindow = new google.maps.InfoWindow({
      content: `<div><strong>${locationName}</strong></div>`
    });
    
    marker.addListener('click', () => {
      infoWindow.open(map, marker);
    });
    
    // Open info window by default
    infoWindow.open(map, marker);
  }
}

// Custom map styles for a more feminine, professional look
const mapStyles = [
  {
    "featureType": "water",
    "elementType": "geometry",
    "stylers": [
      { "color": "#e9e9e9" },
      { "lightness": 17 }
    ]
  },
  {
    "featureType": "landscape",
    "elementType": "geometry",
    "stylers": [
      { "color": "#f5f5f5" },
      { "lightness": 20 }
    ]
  },
  {
    "featureType": "road.highway",
    "elementType": "geometry.fill",
    "stylers": [
      { "color": "#ffffff" },
      { "lightness": 17 }
    ]
  },
  {
    "featureType": "road.highway",
    "elementType": "geometry.stroke",
    "stylers": [
      { "color": "#ffffff" },
      { "lightness": 29 },
      { "weight": 0.2 }
    ]
  },
  {
    "featureType": "road.arterial",
    "elementType": "geometry",
    "stylers": [
      { "color": "#ffffff" },
      { "lightness": 18 }
    ]
  },
  {
    "featureType": "road.local",
    "elementType": "geometry",
    "stylers": [
      { "color": "#ffffff" },
      { "lightness": 16 }
    ]
  },
  {
    "featureType": "poi",
    "elementType": "geometry",
    "stylers": [
      { "color": "#f5f5f5" },
      { "lightness": 21 }
    ]
  },
  {
    "featureType": "poi.park",
    "elementType": "geometry",
    "stylers": [
      { "color": "#dedede" },
      { "lightness": 21 }
    ]
  },
  {
    "elementType": "labels.text.stroke",
    "stylers": [
      { "visibility": "on" },
      { "color": "#ffffff" },
      { "lightness": 16 }
    ]
  },
  {
    "elementType": "labels.text.fill",
    "stylers": [
      { "saturation": 36 },
      { "color": "#333333" },
      { "lightness": 40 }
    ]
  },
  {
    "elementType": "labels.icon",
    "stylers": [
      { "visibility": "off" }
    ]
  },
  {
    "featureType": "administrative",
    "elementType": "geometry.fill",
    "stylers": [
      { "color": "#fefefe" },
      { "lightness": 20 }
    ]
  },
  {
    "featureType": "administrative",
    "elementType": "geometry.stroke",
    "stylers": [
      { "color": "#fefefe" },
      { "lightness": 17 },
      { "weight": 1.2 }
    ]
  }
];
