"""
E-commerce routes for Women Entrepreneurs Hub.
Handles product listings, cart functionality, and checkout.
"""
import logging
from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from app import db, firestore_db
from models import User, Product, Order, OrderItem
import firebase_admin

bp = Blueprint('e_commerce', __name__, url_prefix='/e-commerce')

@bp.route('/', methods=['GET'])
def index():
    """Render the e-commerce homepage with product listings."""
    # Get category filter from query parameters
    category = request.args.get('category')
    
    # Get products from database
    products = []
    
    try:
        # Query products from the database
        if category:
            products_query = Product.query.filter_by(category=category, is_available=True)
        else:
            products_query = Product.query.filter_by(is_available=True)
        
        # Add pagination
        page = request.args.get('page', 1, type=int)
        per_page = 12  # Number of products per page
        pagination = products_query.paginate(page=page, per_page=per_page, error_out=False)
        products = pagination.items
        
        return render_template(
            'e-commerce.html',
            products=products,
            category=category,
            pagination=pagination
        )
    
    except Exception as e:
        logging.error(f"Error loading e-commerce page: {e}")
        return render_template(
            'e-commerce.html',
            products=[],
            category=category,
            error="An error occurred while loading products."
        )

@bp.route('/search', methods=['GET'])
def search():
    """Search for products."""
    query = request.args.get('q', '')
    
    if not query:
        return redirect(url_for('e_commerce.index'))
    
    try:
        # Search for products by name or description
        products_query = Product.query.filter(
            (Product.name.ilike(f'%{query}%') | 
             Product.description.ilike(f'%{query}%')) &
            (Product.is_available == True)
        )
        
        # Add pagination
        page = request.args.get('page', 1, type=int)
        per_page = 12  # Number of products per page
        pagination = products_query.paginate(page=page, per_page=per_page, error_out=False)
        products = pagination.items
        
        return render_template(
            'e-commerce.html',
            products=products,
            query=query,
            pagination=pagination
        )
    
    except Exception as e:
        logging.error(f"Error searching products: {e}")
        return render_template(
            'e-commerce.html',
            products=[],
            query=query,
            error="An error occurred while searching for products."
        )

@bp.route('/product/<int:product_id>', methods=['GET'])
def view_product(product_id):
    """View a single product."""
    try:
        # Get product from database
        product = Product.query.get_or_404(product_id)
        
        # Get similar products
        similar_products = Product.query.filter_by(
            category=product.category, 
            is_available=True
        ).filter(
            Product.id != product_id
        ).limit(4).all()
        
        return render_template(
            'product.html',
            product=product,
            similar_products=similar_products
        )
    
    except Exception as e:
        logging.error(f"Error viewing product {product_id}: {e}")
        return redirect(url_for('e_commerce.index'))

@bp.route('/cart', methods=['GET'])
def view_cart():
    """View the shopping cart."""
    return render_template('cart.html')

@bp.route('/checkout', methods=['GET'])
def checkout():
    """Checkout page."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return redirect(url_for('auth.login'))
    
    return render_template('checkout.html', user_data=user_data)

@bp.route('/add-product', methods=['GET'])
def add_product_form():
    """Render the add product form."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return redirect(url_for('auth.login'))
    
    return render_template('add-product.html', user_data=user_data)

@bp.route('/my-products', methods=['GET'])
def my_products():
    """View the current user's products."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return redirect(url_for('auth.login'))
    
    try:
        # Get user's products
        user_id = user_data.get('id')
        products = Product.query.filter_by(user_id=user_id).all()
        
        return render_template(
            'my-products.html',
            products=products,
            user_data=user_data
        )
    
    except Exception as e:
        logging.error(f"Error loading user products: {e}")
        return render_template(
            'my-products.html',
            products=[],
            user_data=user_data,
            error="An error occurred while loading your products."
        )

@bp.route('/edit-product/<int:product_id>', methods=['GET'])
def edit_product(product_id):
    """Render the edit product form."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return redirect(url_for('auth.login'))
    
    try:
        # Get product from database
        product = Product.query.get_or_404(product_id)
        
        # Check if the product belongs to the current user
        if product.user_id != user_data.get('id'):
            return redirect(url_for('e_commerce.my_products'))
        
        return render_template(
            'edit-product.html',
            product=product,
            user_data=user_data
        )
    
    except Exception as e:
        logging.error(f"Error loading product for editing: {e}")
        return redirect(url_for('e_commerce.my_products'))

@bp.route('/orders', methods=['GET'])
def my_orders():
    """View the current user's orders."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return redirect(url_for('auth.login'))
    
    try:
        # Get user's orders
        user_id = user_data.get('id')
        orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
        
        return render_template(
            'orders.html',
            orders=orders,
            user_data=user_data
        )
    
    except Exception as e:
        logging.error(f"Error loading user orders: {e}")
        return render_template(
            'orders.html',
            orders=[],
            user_data=user_data,
            error="An error occurred while loading your orders."
        )

@bp.route('/orders/<order_id>', methods=['GET'])
def view_order(order_id):
    """View a single order."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return redirect(url_for('auth.login'))
    
    try:
        # If it's a Firebase ID, get the order from Firestore
        if firestore_db and not order_id.isdigit():
            order_doc = firestore_db.collection('orders').document(order_id).get()
            if not order_doc.exists:
                return redirect(url_for('e_commerce.my_orders'))
            
            order_data = order_doc.to_dict()
            
            # Check if the order belongs to the current user
            if order_data.get('user_id') != user_data.get('firebase_uid'):
                return redirect(url_for('e_commerce.my_orders'))
            
            return render_template(
                'order-details.html',
                order=order_data,
                order_id=order_id,
                user_data=user_data,
                is_firestore=True
            )
        else:
            # Get order from database
            order = Order.query.get_or_404(order_id)
            
            # Check if the order belongs to the current user
            if order.user_id != user_data.get('id'):
                return redirect(url_for('e_commerce.my_orders'))
            
            return render_template(
                'order-details.html',
                order=order,
                user_data=user_data,
                is_firestore=False
            )
    
    except Exception as e:
        logging.error(f"Error viewing order {order_id}: {e}")
        return redirect(url_for('e_commerce.my_orders'))

@bp.route('/api/products', methods=['POST'])
def create_product():
    """Create a new product."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        # Get JSON data
        data = request.json
        
        # Validate required fields
        required_fields = ['name', 'price']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        
        # Get user ID
        user_id = user_data.get('id')
        
        # Create new product
        product = Product(
            user_id=user_id,
            firebase_id=data.get('firebase_id'),
            name=data.get('name'),
            description=data.get('description', ''),
            price=float(data.get('price')),
            image_url=data.get('image_url'),
            category=data.get('category'),
            stock=int(data.get('stock', 0)),
            is_available=True
        )
        
        # Add to database
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Product created successfully',
            'product_id': product.id
        })
    
    except Exception as e:
        logging.error(f"Error creating product: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    """Update an existing product."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        # Get product from database
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'success': False, 'message': 'Product not found'}), 404
        
        # Check if the product belongs to the current user
        if product.user_id != user_data.get('id'):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        # Get JSON data
        data = request.json
        
        # Update product fields
        if 'name' in data:
            product.name = data.get('name')
        
        if 'description' in data:
            product.description = data.get('description')
        
        if 'price' in data:
            product.price = float(data.get('price'))
        
        if 'image_url' in data:
            product.image_url = data.get('image_url')
        
        if 'category' in data:
            product.category = data.get('category')
        
        if 'stock' in data:
            product.stock = int(data.get('stock'))
        
        if 'is_available' in data:
            product.is_available = bool(data.get('is_available'))
        
        # Update database
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Product updated successfully'
        })
    
    except Exception as e:
        logging.error(f"Error updating product {product_id}: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        # Get product from database
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'success': False, 'message': 'Product not found'}), 404
        
        # Check if the product belongs to the current user
        if product.user_id != user_data.get('id'):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        # Delete from database
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Product deleted successfully'
        })
    
    except Exception as e:
        logging.error(f"Error deleting product {product_id}: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/orders', methods=['POST'])
def create_order():
    """Create a new order."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        # Get JSON data
        data = request.json
        
        # Validate required fields
        required_fields = ['items', 'total_amount']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        
        # Get user ID
        user_id = user_data.get('id')
        
        # Create new order
        order = Order(
            user_id=user_id,
            firebase_id=data.get('firebase_id'),
            total_amount=float(data.get('total_amount')),
            status=data.get('status', 'pending'),
            payment_method=data.get('payment_method'),
            payment_id=data.get('payment_id'),
            shipping_address=data.get('shipping_address')
        )
        
        # Add to database
        db.session.add(order)
        db.session.commit()
        
        # Create order items
        items = data.get('items', [])
        for item in items:
            # Get product by Firebase ID or regular ID
            product = None
            if 'id' in item:
                if isinstance(item['id'], str) and not item['id'].isdigit():
                    # This is a Firebase ID, find the product in our database
                    product = Product.query.filter_by(firebase_id=item['id']).first()
                else:
                    # This is a regular ID
                    product = Product.query.get(item['id'])
            
            if product:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=int(item.get('quantity', 1)),
                    price=float(item.get('price', product.price))
                )
                db.session.add(order_item)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Order created successfully',
            'order_id': order.id
        })
    
    except Exception as e:
        logging.error(f"Error creating order: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
