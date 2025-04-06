document.addEventListener('DOMContentLoaded', function() {
  // Product image upload
  const imageUploadForm = document.getElementById('image-upload-form');
  if (imageUploadForm) {
    const productId = imageUploadForm.dataset.productId;
    const imageInput = document.getElementById('product-image');
    const uploadButton = document.getElementById('upload-image-btn');
    const imageGallery = document.getElementById('image-gallery');
    
    uploadButton.addEventListener('click', function(e) {
      e.preventDefault();
      
      if (!imageInput.files || imageInput.files.length === 0) {
        alert('Please select an image to upload.');
        return;
      }
      
      const file = imageInput.files[0];
      
      // Check file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('File is too large. Maximum size is 5MB.');
        return;
      }
      
      // Show loading state
      uploadButton.disabled = true;
      uploadButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Uploading...';
      
      // Create form data
      const formData = new FormData();
      formData.append('image', file);
      
      // Upload image
      fetch(`/shop/upload-product-image/${productId}`, {
        method: 'POST',
        body: formData
      })
      .then(response => response.json())
      .then(data => {
        // Reset button state
        uploadButton.disabled = false;
        uploadButton.textContent = 'Upload Image';
        
        if (data.success) {
          // Add image to gallery
          addImageToGallery(data.image_url);
          // Clear file input
          imageInput.value = '';
        } else {
          alert(`Error: ${data.message}`);
        }
      })
      .catch(error => {
        console.error('Error uploading image:', error);
        alert('Error uploading image. Please try again.');
        
        // Reset button state
        uploadButton.disabled = false;
        uploadButton.textContent = 'Upload Image';
      });
    });
    
    // Function to add image to gallery
    function addImageToGallery(imageUrl) {
      const col = document.createElement('div');
      col.className = 'col-md-4 col-sm-6 mb-3';
      
      col.innerHTML = `
        <div class="card h-100">
          <img src="${imageUrl}" class="card-img-top" alt="Product image">
          <div class="card-body text-center">
            <button class="btn btn-sm btn-danger remove-image" data-image-url="${imageUrl}">
              <i class="fas fa-trash-alt"></i> Remove
            </button>
          </div>
        </div>
      `;
      
      imageGallery.appendChild(col);
      
      // Add event listener to remove button
      col.querySelector('.remove-image').addEventListener('click', function() {
        removeProductImage(this.dataset.imageUrl, col);
      });
    }
    
    // Function to remove image
    function removeProductImage(imageUrl, element) {
      if (confirm('Are you sure you want to remove this image?')) {
        fetch(`/shop/remove-product-image/${productId}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ image_url: imageUrl })
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            // Remove image element from DOM
            element.remove();
          } else {
            alert(`Error: ${data.message}`);
          }
        })
        .catch(error => {
          console.error('Error removing image:', error);
          alert('Error removing image. Please try again.');
        });
      }
    }
    
    // Add event listeners to existing remove buttons
    document.querySelectorAll('.remove-image').forEach(button => {
      button.addEventListener('click', function() {
        const imageUrl = this.dataset.imageUrl;
        const col = this.closest('.col-md-4');
        removeProductImage(imageUrl, col);
      });
    });
  }
  
  // Product deletion
  const deleteProductButtons = document.querySelectorAll('.delete-product');
  deleteProductButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      
      const productId = this.dataset.productId;
      const productName = this.dataset.productName;
      
      if (confirm(`Are you sure you want to delete the product "${productName}"?`)) {
        // Show loading state
        this.disabled = true;
        this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
        
        fetch(`/shop/delete-product/${productId}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          }
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            // Remove product row from table
            this.closest('tr').remove();
            
            // Show success message
            const alertContainer = document.createElement('div');
            alertContainer.className = 'alert alert-success alert-dismissible fade show';
            alertContainer.innerHTML = `
              ${data.message}
              <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            
            document.querySelector('.container').prepend(alertContainer);
          } else {
            alert(`Error: ${data.message}`);
            
            // Reset button state
            this.disabled = false;
            this.innerHTML = '<i class="fas fa-trash-alt"></i>';
          }
        })
        .catch(error => {
          console.error('Error deleting product:', error);
          alert('Error deleting product. Please try again.');
          
          // Reset button state
          this.disabled = false;
          this.innerHTML = '<i class="fas fa-trash-alt"></i>';
        });
      }
    });
  });
  
  // Google Pay integration
  const googlePayButtons = document.querySelectorAll('.google-pay-button');
  googlePayButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      
      const productId = this.dataset.productId;
      const productName = this.dataset.productName;
      const productPrice = parseFloat(this.dataset.productPrice);
      
      // Simple mock for Google Pay integration
      // In a real implementation, this would use the Google Pay API
      alert(`Google Pay integration would process payment of $${productPrice.toFixed(2)} for ${productName}.`);
    });
  });
  
  // Shopping cart functionality
  const addToCartButtons = document.querySelectorAll('.add-to-cart');
  const cartItems = JSON.parse(localStorage.getItem('cartItems') || '[]');
  
  // Update cart counter
  updateCartCounter();
  
  addToCartButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      
      const productId = this.dataset.productId;
      const productName = this.dataset.productName;
      const productPrice = parseFloat(this.dataset.productPrice);
      const productImage = this.dataset.productImage;
      
      // Add item to cart
      const item = {
        id: productId,
        name: productName,
        price: productPrice,
        image: productImage,
        quantity: 1
      };
      
      // Check if item already exists in cart
      const existingItemIndex = cartItems.findIndex(i => i.id === productId);
      
      if (existingItemIndex !== -1) {
        // Increment quantity
        cartItems[existingItemIndex].quantity += 1;
      } else {
        // Add new item
        cartItems.push(item);
      }
      
      // Save cart to localStorage
      localStorage.setItem('cartItems', JSON.stringify(cartItems));
      
      // Show success message
      const toast = document.createElement('div');
      toast.className = 'toast align-items-center text-white bg-success border-0';
      toast.setAttribute('role', 'alert');
      toast.setAttribute('aria-live', 'assertive');
      toast.setAttribute('aria-atomic', 'true');
      
      toast.innerHTML = `
        <div class="d-flex">
          <div class="toast-body">
            <strong>${productName}</strong> added to cart!
          </div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
      `;
      
      document.body.appendChild(toast);
      
      const bsToast = new bootstrap.Toast(toast);
      bsToast.show();
      
      // Update cart counter
      updateCartCounter();
    });
  });
  
  // Function to update cart counter
  function updateCartCounter() {
    const cartCounter = document.getElementById('cart-counter');
    if (cartCounter) {
      const totalItems = cartItems.reduce((total, item) => total + item.quantity, 0);
      cartCounter.textContent = totalItems;
      
      if (totalItems > 0) {
        cartCounter.classList.remove('d-none');
      } else {
        cartCounter.classList.add('d-none');
      }
    }
  }
  
  // Render cart items on cart page
  const cartItemsContainer = document.getElementById('cart-items');
  if (cartItemsContainer) {
    if (cartItems.length === 0) {
      cartItemsContainer.innerHTML = `
        <div class="text-center my-5">
          <h3>Your cart is empty</h3>
          <p>Start shopping to add items to your cart.</p>
          <a href="/shop" class="btn btn-primary">Browse Products</a>
        </div>
      `;
    } else {
      // Calculate total
      const total = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
      
      cartItemsContainer.innerHTML = `
        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>Product</th>
                <th>Price</th>
                <th>Quantity</th>
                <th>Total</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              ${cartItems.map(item => `
                <tr>
                  <td>
                    <div class="d-flex align-items-center">
                      <img src="${item.image || '/static/img/no-image.svg'}" alt="${item.name}" class="img-thumbnail me-3" style="width: 60px; height: 60px; object-fit: cover;">
                      <span>${item.name}</span>
                    </div>
                  </td>
                  <td>$${item.price.toFixed(2)}</td>
                  <td>
                    <div class="input-group" style="width: 100px;">
                      <button class="btn btn-outline-secondary decrease-quantity" data-product-id="${item.id}" type="button">-</button>
                      <input type="text" class="form-control text-center item-quantity" value="${item.quantity}" readonly>
                      <button class="btn btn-outline-secondary increase-quantity" data-product-id="${item.id}" type="button">+</button>
                    </div>
                  </td>
                  <td>$${(item.price * item.quantity).toFixed(2)}</td>
                  <td>
                    <button class="btn btn-sm btn-danger remove-cart-item" data-product-id="${item.id}">
                      <i class="fas fa-trash-alt"></i>
                    </button>
                  </td>
                </tr>
              `).join('')}
            </tbody>
            <tfoot>
              <tr>
                <td colspan="3" class="text-end"><strong>Total:</strong></td>
                <td>$${total.toFixed(2)}</td>
                <td></td>
              </tr>
            </tfoot>
          </table>
        </div>
        
        <div class="d-flex justify-content-between mt-4">
          <a href="/shop" class="btn btn-outline-primary">Continue Shopping</a>
          <button id="checkout-button" class="btn btn-success">Proceed to Checkout</button>
        </div>
      `;
      
      // Add event listeners for cart interactions
      document.querySelectorAll('.decrease-quantity').forEach(button => {
        button.addEventListener('click', function() {
          updateItemQuantity(this.dataset.productId, -1);
        });
      });
      
      document.querySelectorAll('.increase-quantity').forEach(button => {
        button.addEventListener('click', function() {
          updateItemQuantity(this.dataset.productId, 1);
        });
      });
      
      document.querySelectorAll('.remove-cart-item').forEach(button => {
        button.addEventListener('click', function() {
          removeCartItem(this.dataset.productId);
        });
      });
      
      // Checkout button
      document.getElementById('checkout-button').addEventListener('click', function() {
        // In a real implementation, this would redirect to a checkout page or process
        alert('Checkout functionality would be implemented here with Google Pay integration.');
      });
    }
  }
  
  // Function to update item quantity
  function updateItemQuantity(productId, change) {
    const itemIndex = cartItems.findIndex(item => item.id === productId);
    
    if (itemIndex !== -1) {
      cartItems[itemIndex].quantity += change;
      
      // Remove item if quantity is 0 or less
      if (cartItems[itemIndex].quantity <= 0) {
        cartItems.splice(itemIndex, 1);
      }
      
      // Save updated cart
      localStorage.setItem('cartItems', JSON.stringify(cartItems));
      
      // Refresh cart page
      if (document.getElementById('cart-items')) {
        location.reload();
      }
      
      // Update cart counter
      updateCartCounter();
    }
  }
  
  // Function to remove cart item
  function removeCartItem(productId) {
    const itemIndex = cartItems.findIndex(item => item.id === productId);
    
    if (itemIndex !== -1) {
      cartItems.splice(itemIndex, 1);
      
      // Save updated cart
      localStorage.setItem('cartItems', JSON.stringify(cartItems));
      
      // Refresh cart page
      if (document.getElementById('cart-items')) {
        location.reload();
      }
      
      // Update cart counter
      updateCartCounter();
    }
  }
});
