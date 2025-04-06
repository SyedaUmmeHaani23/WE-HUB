// Enhanced animations and interactions for Women Entrepreneurs Hub
document.addEventListener('DOMContentLoaded', function() {
    // Navbar scroll effect
    const navbar = document.querySelector('.navbar-we');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // Add animation classes to elements when they come into view
    const animateOnScroll = function() {
        const elements = document.querySelectorAll('.animate-on-scroll:not(.animated)');
        
        elements.forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const screenPosition = window.innerHeight;
            
            if (elementPosition < screenPosition - 100) {
                // Add the animation class based on data attribute
                const animationType = element.dataset.animation || 'fade-in';
                element.classList.add(animationType, 'animated');
            }
        });
    };

    // Run animation check on load and scroll
    window.addEventListener('load', animateOnScroll);
    window.addEventListener('scroll', animateOnScroll);

    // Hero parallax effect
    const heroSection = document.querySelector('.hero-section');
    if (heroSection) {
        window.addEventListener('scroll', function() {
            const scrollPosition = window.scrollY;
            if (scrollPosition < 600) {
                heroSection.style.backgroundPosition = `center ${scrollPosition * 0.5}px`;
            }
        });
    }

    // Add floating animation to specified elements
    document.querySelectorAll('.float-element').forEach(element => {
        element.classList.add('float-animation');
    });

    // Add pulse animation to specified elements
    document.querySelectorAll('.pulse-element').forEach(element => {
        element.classList.add('pulse-animation');
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Interactive feature cards
    document.querySelectorAll('.feature-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.querySelector('.feature-icon').classList.add('animated');
        });
        
        card.addEventListener('mouseleave', function() {
            this.querySelector('.feature-icon').classList.remove('animated');
        });
    });

    // Success stories carousel auto-scroll
    const successStoriesContainer = document.querySelector('.success-stories-container');
    if (successStoriesContainer) {
        let scrollPosition = 0;
        const totalWidth = successStoriesContainer.scrollWidth;
        const visibleWidth = successStoriesContainer.offsetWidth;
        
        const scrollSuccessStories = () => {
            scrollPosition += 1;
            if (scrollPosition > totalWidth - visibleWidth) {
                scrollPosition = 0;
            }
            successStoriesContainer.scrollLeft = scrollPosition;
        };
        
        // Pause auto scroll on hover
        successStoriesContainer.addEventListener('mouseenter', () => {
            clearInterval(successStoriesInterval);
        });
        
        successStoriesContainer.addEventListener('mouseleave', () => {
            successStoriesInterval = setInterval(scrollSuccessStories, 30);
        });
        
        let successStoriesInterval = setInterval(scrollSuccessStories, 30);
    }

    // Counters animation for statistics
    const animateCounters = () => {
        document.querySelectorAll('.stats-value[data-count]').forEach(counter => {
            const target = parseInt(counter.getAttribute('data-count'));
            const duration = 2000; // ms
            const increment = target / (duration / 16); // 60fps
            
            let current = 0;
            const animate = () => {
                current += increment;
                counter.textContent = Math.floor(current);
                
                if (current < target) {
                    requestAnimationFrame(animate);
                } else {
                    counter.textContent = target;
                }
            };
            
            animate();
        });
    };

    // Only animate counters when they're in view
    const statsSection = document.querySelector('.stats-section');
    if (statsSection) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounters();
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        
        observer.observe(statsSection);
    }

    // Testimonial/Reviews rotation
    const testimonials = document.querySelectorAll('.testimonial-card');
    if (testimonials.length > 1) {
        let currentTestimonial = 0;
        
        const showNextTestimonial = () => {
            testimonials[currentTestimonial].classList.remove('active');
            currentTestimonial = (currentTestimonial + 1) % testimonials.length;
            testimonials[currentTestimonial].classList.add('active');
        };
        
        // Start with the first testimonial active
        testimonials[0].classList.add('active');
        
        // Rotate testimonials every 5 seconds
        setInterval(showNextTestimonial, 5000);
    }

    // Product image gallery for product detail page
    const productThumbnails = document.querySelectorAll('.product-thumbnail');
    const productMainImage = document.querySelector('.product-main-image');
    
    if (productThumbnails.length && productMainImage) {
        productThumbnails.forEach(thumbnail => {
            thumbnail.addEventListener('click', function() {
                // Remove active class from all thumbnails
                productThumbnails.forEach(thumb => thumb.classList.remove('active'));
                
                // Add active class to clicked thumbnail
                this.classList.add('active');
                
                // Update main image
                productMainImage.src = this.dataset.image;
                productMainImage.classList.add('image-change');
                
                // Remove animation class after animation completes
                setTimeout(() => {
                    productMainImage.classList.remove('image-change');
                }, 500);
            });
        });
    }

    // Add to cart animation
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
    if (addToCartButtons.length) {
        addToCartButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Create a flying cart item element
                const cartIcon = document.querySelector('.fa-shopping-cart');
                if (!cartIcon) return;
                
                const flyingItem = document.createElement('div');
                flyingItem.className = 'flying-item';
                
                // Position it at the button
                const buttonRect = this.getBoundingClientRect();
                flyingItem.style.top = buttonRect.top + 'px';
                flyingItem.style.left = buttonRect.left + 'px';
                
                document.body.appendChild(flyingItem);
                
                // Get the cart icon position
                const cartRect = cartIcon.getBoundingClientRect();
                
                // Animate the flying item to the cart
                setTimeout(() => {
                    flyingItem.style.top = cartRect.top + 'px';
                    flyingItem.style.left = cartRect.left + 'px';
                    flyingItem.style.opacity = '0';
                    flyingItem.style.transform = 'scale(0.1)';
                    
                    // Update cart count
                    setTimeout(() => {
                        document.body.removeChild(flyingItem);
                        
                        // Make cart icon pop
                        cartIcon.classList.add('cart-pop');
                        setTimeout(() => {
                            cartIcon.classList.remove('cart-pop');
                        }, 300);
                        
                        // Increment cart count if exists
                        const cartCount = document.getElementById('cart-count');
                        if (cartCount) {
                            cartCount.style.display = 'inline';
                            let count = parseInt(cartCount.textContent);
                            if (isNaN(count)) count = 0;
                            cartCount.textContent = count + 1;
                        }
                    }, 500);
                }, 10);
            });
        });
    }
});
