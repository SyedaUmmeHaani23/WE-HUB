// E-commerce functionality for Women Entrepreneurs Hub
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

// Create a cart in localStorage if it doesn't exist
if (!localStorage.getItem('cart')) {
  localStorage.setItem('cart', JSON.stringify([]));
}

// Functions for product management
const productService = {
  // Get all products
  getAllProducts: async () => {
    try {
      const productsRef = collection(db, 'products');
      const q = query(productsRef, where('is_available', '==', true), orderBy('created_at', 'desc'));
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
      console.error('Error getting products:', error);
      return [];
    }
  },
  
  // Get products by user ID
  getProductsByUser: async (userId) => {
    try {
      const productsRef = collection(db, 'products');
      const q = query(productsRef, where('user_id', '==', userId));
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
      console.error('Error getting user products:', error);
      return [];
    }
  },
  
  // Get product by ID
  getProduct: async (productId) => {
    try {
      const productRef = doc(db, 'products', productId);
      const productSnap = await getDoc(productRef);
      
      if (productSnap.exists()) {
        return {
          id: productSnap.id,
          ...productSnap.data()
        };
      } else {
        console.error('Product not found');
        return null;
      }
    } catch (error) {
      console.error('Error getting product:', error);
      return null;
    }
  },
  
  // Add a new product
  addProduct: async (productData, imageFile) => {
    try {
      if (!auth.currentUser) {
        throw new Error('User must be authenticated to add products');
      }
      
      // Upload image if provided
      let imageUrl = null;
      if (imageFile) {
        const storageRef = ref(storage, `product_images/${auth.currentUser.uid}/${Date.now()}_${imageFile.name}`);
        await uploadBytes(storageRef, imageFile);
        imageUrl = await getDownloadURL(storageRef);
      }
      
      // Add product to Firestore
      const newProduct = {
        ...productData,
        user_id: auth.currentUser.uid,
        image_url: imageUrl,
        created_at: new Date(),
        updated_at: new Date(),
        is_available: true
      };
      
      const docRef = await addDoc(collection(db, 'products'), newProduct);
      
      // Send to backend to sync
      await fetch('/api/products', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...newProduct,
          firebase_id: docRef.id
        }),
      });
      
      return docRef.id;
    } catch (error) {
      console.error('Error adding product:', error);
      throw error;
    }
  },
  
  // Update a product
  updateProduct: async (productId, productData, imageFile) => {
    try {
      if (!auth.currentUser) {
        throw new Error('User must be authenticated to update products');
      }
      
      // Upload image if provided
      let imageUrl = productData.image_url;
      if (imageFile) {
        const storageRef = ref(storage, `product_images/${auth.currentUser.uid}/${Date.now()}_${imageFile.name}`);
        await uploadBytes(storageRef, imageFile);
        imageUrl = await getDownloadURL(storageRef);
      }
      
      // Update product in Firestore
      const productRef = doc(db, 'products', productId);
      
      const updatedProduct = {
        ...productData,
        image_url: imageUrl,
        updated_at: new Date()
      };
      
      await updateDoc(productRef, updatedProduct);
      
      // Send to backend to sync
      await fetch(`/api/products/${productId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedProduct),
      });
      
      return productId;
    } catch (error) {
      console.error('Error updating product:', error);
      throw error;
    }
  },
  
  // Delete a product
  deleteProduct: async (productId) => {
    try {
      if (!auth.currentUser) {
        throw new Error('User must be authenticated to delete products');
      }
      
      // Delete product from Firestore
      const productRef = doc(db, 'products', productId);
      await deleteDoc(productRef);
      
      // Send to backend to sync
      await fetch(`/api/products/${productId}`, {
        method: 'DELETE'
      });
      
      return true;
    } catch (error) {
      console.error('Error deleting product:', error);
      throw error;
    }
  }
};

// Cart functionality
const cartService = {
  // Get cart items
  getCart: () => {
    return JSON.parse(localStorage.getItem('cart') || '[]');
  },
  
  // Add item to cart
  addToCart: (product, quantity = 1) => {
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    const existingItemIndex = cart.findIndex(item => item.id === product.id);
    
    if (existingItemIndex > -1) {
      // Update quantity if item is already in cart
      cart[existingItemIndex].quantity += quantity;
    } else {
      // Add new item
      cart.push({
        id: product.id,
        name: product.name,
        price: product.price,
        image_url: product.image_url,
        quantity: quantity
      });
    }
    
    localStorage.setItem('cart', JSON.stringify(cart));
    
    // Update cart UI
    updateCartUI();
    
    return cart;
  },
  
  // Update cart item quantity
  updateCartItem: (productId, quantity) => {
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    const itemIndex = cart.findIndex(item => item.id === productId);
    
    if (itemIndex > -1) {
      if (quantity > 0) {
        cart[itemIndex].quantity = quantity;
      } else {
        // Remove item if quantity is 0 or less
        cart.splice(itemIndex, 1);
      }
      
      localStorage.setItem('cart', JSON.stringify(cart));
      
      // Update cart UI
      updateCartUI();
    }
    
    return cart;
  },
  
  // Remove item from cart
  removeFromCart: (productId) => {
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    const updatedCart = cart.filter(item => item.id !== productId);
    
    localStorage.setItem('cart', JSON.stringify(updatedCart));
    
    // Update cart UI
    updateCartUI();
    
    return updatedCart;
  },
  
  // Clear cart
  clearCart: () => {
    localStorage.setItem('cart', JSON.stringify([]));
    
    // Update cart UI
    updateCartUI();
    
    return [];
  },
  
  // Calculate cart total
  getCartTotal: () => {
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    return cart.reduce((total, item) => total + (item.price * item.quantity), 0);
  }
};

// Update cart UI
function updateCartUI() {
  const cart = cartService.getCart();
  const cartCount = document.getElementById('cart-count');
  const cartTotal = document.getElementById('cart-total');
  const cartItems = document.getElementById('cart-items');
  
  if (cartCount) {
    const itemCount = cart.reduce((total, item) => total + item.quantity, 0);
    cartCount.textContent = itemCount;
    
    // Show/hide based on whether cart has items
    if (itemCount > 0) {
      cartCount.style.display = 'inline-block';
    } else {
      cartCount.style.display = 'none';
    }
  }
  
  if (cartTotal) {
    cartTotal.textContent = `$${cartService.getCartTotal().toFixed(2)}`;
  }
  
  if (cartItems) {
    // Clear existing items
    cartItems.innerHTML = '';
    
    if (cart.length === 0) {
      cartItems.innerHTML = '<div class="text-center p-3">Your cart is empty</div>';
    } else {
      // Add each item to the cart UI
      cart.forEach(item => {
        const itemElement = document.createElement('div');
        itemElement.className = 'cart-item d-flex align-items-center p-2 border-bottom';
        
        itemElement.innerHTML = `
          <div class="cart-item-image me-2">
            ${item.image_url ? `<img src="${item.image_url}" alt="${item.name}" width="50" height="50" class="rounded">` : 
            '<div class="bg-secondary rounded" style="width:50px;height:50px;"></div>'}
          </div>
          <div class="cart-item-details flex-grow-1">
            <div class="cart-item-name">${item.name}</div>
            <div class="cart-item-price">$${item.price.toFixed(2)} x ${item.quantity}</div>
          </div>
          <div class="cart-item-actions">
            <button class="btn btn-sm btn-outline-danger remove-from-cart" data-product-id="${item.id}">
              <i class="fa fa-trash"></i>
            </button>
          </div>
        `;
        
        cartItems.appendChild(itemElement);
        
        // Add event listener to remove button
        const removeButton = itemElement.querySelector('.remove-from-cart');
        removeButton.addEventListener('click', () => {
          cartService.removeFromCart(item.id);
        });
      });
    }
  }
}

// Initialize Google Pay
function initGooglePay() {
  // Load Google Pay API if available
  if (window.google && window.google.payments) {
    const googlePayClient = new google.payments.api.PaymentsClient({
      environment: 'TEST' // Change to 'PRODUCTION' for real payments
    });
    
    const baseRequest = {
      apiVersion: 2,
      apiVersionMinor: 0
    };
    
    const allowedPaymentMethods = [{
      type: 'CARD',
      parameters: {
        allowedAuthMethods: ['PAN_ONLY', 'CRYPTOGRAM_3DS'],
        allowedCardNetworks: ['AMEX', 'DISCOVER', 'MASTERCARD', 'VISA']
      },
      tokenizationSpecification: {
        type: 'PAYMENT_GATEWAY',
        parameters: {
          gateway: 'example',
          gatewayMerchantId: 'exampleGatewayMerchantId'
        }
      }
    }];
    
    const isReadyToPayRequest = Object.assign({}, baseRequest);
    isReadyToPayRequest.allowedPaymentMethods = allowedPaymentMethods;
    
    // Check if Google Pay is available
    googlePayClient.isReadyToPay(isReadyToPayRequest)
      .then(response => {
        if (response.result) {
          // Google Pay is available
          const button = document.getElementById('google-pay-button');
          if (button) {
            button.style.display = 'block';
            
            // Create Google Pay button
            googlePayClient.createButton({
              onClick: () => {
                // Create payment data request
                const paymentDataRequest = Object.assign({}, baseRequest);
                paymentDataRequest.allowedPaymentMethods = allowedPaymentMethods;
                paymentDataRequest.transactionInfo = {
                  totalPriceStatus: 'FINAL',
                  totalPrice: cartService.getCartTotal().toString(),
                  currencyCode: 'USD',
                  countryCode: 'US'
                };
                paymentDataRequest.merchantInfo = {
                  merchantName: 'Women Entrepreneurs Hub'
                };
                
                // Show Google Pay payment sheet
                googlePayClient.loadPaymentData(paymentDataRequest)
                  .then(paymentData => {
                    // Process payment data
                    console.log('Payment successful:', paymentData);
                    
                    // Create order
                    createOrder(paymentData);
                  })
                  .catch(error => {
                    console.error('Error processing payment:', error);
                  });
              }
            });
          }
        }
      })
      .catch(error => {
        console.error('Error checking Google Pay availability:', error);
      });
  }
}

// Create order after successful payment
async function createOrder(paymentData) {
  try {
    if (!auth.currentUser) {
      throw new Error('User must be authenticated to place an order');
    }
    
    const cart = cartService.getCart();
    
    if (cart.length === 0) {
      throw new Error('Cannot create order with empty cart');
    }
    
    // Create order in Firestore
    const order = {
      user_id: auth.currentUser.uid,
      items: cart,
      total_amount: cartService.getCartTotal(),
      status: 'completed',
      payment_method: 'Google Pay',
      payment_id: paymentData.paymentMethodData.tokenizationData.token,
      created_at: new Date(),
      updated_at: new Date()
    };
    
    const orderRef = await addDoc(collection(db, 'orders'), order);
    
    // Send to backend to sync
    await fetch('/api/orders', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...order,
        firebase_id: orderRef.id
      }),
    });
    
    // Clear cart
    cartService.clearCart();
    
    // Show success message
    alert('Order placed successfully!');
    
    // Redirect to order confirmation page
    window.location.href = `/orders/${orderRef.id}`;
  } catch (error) {
    console.error('Error creating order:', error);
    alert(`Error placing order: ${error.message}`);
  }
}

// Initialize e-commerce functionality when document is loaded
document.addEventListener('DOMContentLoaded', () => {
  // Update cart UI
  updateCartUI();
  
  // Initialize Google Pay
  if (document.getElementById('google-pay-button')) {
    initGooglePay();
  }
  
  // Handle add to cart buttons
  document.querySelectorAll('.add-to-cart').forEach(button => {
    button.addEventListener('click', async (e) => {
      const productId = e.target.getAttribute('data-product-id');
      const product = await productService.getProduct(productId);
      if (product) {
        cartService.addToCart(product);
        
        // Show success message
        const toast = new bootstrap.Toast(document.getElementById('cart-toast'));
        toast.show();
      }
    });
  });
  
  // Handle product form submission
  const productForm = document.getElementById('product-form');
  if (productForm) {
    productForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const formData = new FormData(productForm);
      const productData = {
        name: formData.get('name'),
        description: formData.get('description'),
        price: parseFloat(formData.get('price')),
        category: formData.get('category'),
        stock: parseInt(formData.get('stock'))
      };
      
      const imageFile = formData.get('image');
      const productId = formData.get('product_id');
      
      try {
        if (productId) {
          // Update existing product
          await productService.updateProduct(productId, productData, imageFile.size > 0 ? imageFile : null);
          alert('Product updated successfully!');
        } else {
          // Add new product
          await productService.addProduct(productData, imageFile.size > 0 ? imageFile : null);
          alert('Product added successfully!');
          productForm.reset();
        }
      } catch (error) {
        alert(`Error: ${error.message}`);
      }
    });
  }
  
  // Handle proceed to checkout button
  const checkoutButton = document.getElementById('checkout-button');
  if (checkoutButton) {
    checkoutButton.addEventListener('click', () => {
      if (!auth.currentUser) {
        alert('Please sign in to checkout');
        return;
      }
      
      if (cartService.getCart().length === 0) {
        alert('Your cart is empty');
        return;
      }
      
      window.location.href = '/checkout';
    });
  }
});

// Export cart and product services
window.cartService = cartService;
window.productService = productService;
