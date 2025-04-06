import logging
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from models import Product
from app import db
import uuid
import os
from datetime import datetime
from werkzeug.utils import secure_filename

# Import Firebase storage bucket from app.py
try:
    from app import bucket, firestore_db
except ImportError:
    # For when the app is starting and Firebase isn't fully initialized
    bucket = None
    firestore_db = None

ecommerce_bp = Blueprint('ecommerce', __name__, url_prefix='/shop')

@ecommerce_bp.route('/')
def shop():
    """Main shop page displaying all products"""
    try:
        # Get all products from Firestore
        products = []
        if db:
            product_docs = db.collection('products').where('in_stock', '==', True).stream()
            
            for doc in product_docs:
                product_data = doc.to_dict()
                products.append({
                    'id': doc.id,
                    'name': product_data.get('name'),
                    'description': product_data.get('description'),
                    'price': product_data.get('price'),
                    'category': product_data.get('category'),
                    'images': product_data.get('images', []),
                    'user_id': product_data.get('user_id')
                })
                
            # Get seller information for each product
            for product in products:
                seller_doc = db.collection('users').document(product['user_id']).get()
                if seller_doc.exists:
                    seller_data = seller_doc.to_dict()
                    product['seller'] = {
                        'name': seller_data.get('business_data', {}).get('name') or seller_data.get('display_name'),
                        'photo': seller_data.get('photo_url')
                    }
                
        return render_template('ecommerce/shop.html', products=products)
    
    except Exception as e:
        logging.error(f"Error loading shop: {e}")
        flash("Error loading shop. Please try again later.", "danger")
        return render_template('ecommerce/shop.html', products=[])

@ecommerce_bp.route('/product/<product_id>')
def product_detail(product_id):
    """Product detail page"""
    try:
        product = Product.get(product_id)
        if not product:
            flash("Product not found.", "warning")
            return redirect(url_for('ecommerce.shop'))
            
        # Get seller information
        seller = None
        if db:
            seller_doc = db.collection('users').document(product.user_id).get()
            if seller_doc.exists:
                seller_data = seller_doc.to_dict()
                seller = {
                    'id': product.user_id,
                    'name': seller_data.get('business_data', {}).get('name') or seller_data.get('display_name'),
                    'photo': seller_data.get('photo_url'),
                    'business': seller_data.get('business_data', {})
                }
                
        return render_template('ecommerce/product.html', product=product, seller=seller)
    
    except Exception as e:
        logging.error(f"Error loading product details: {e}")
        flash("Error loading product details. Please try again later.", "danger")
        return redirect(url_for('ecommerce.shop'))

@ecommerce_bp.route('/cart')
@login_required
def cart():
    """Shopping cart page"""
    return render_template('ecommerce/cart.html')

@ecommerce_bp.route('/my-products')
@login_required
def my_products():
    """List user's products for management"""
    try:
        products = Product.get_by_user(current_user.id)
        return render_template('ecommerce/my_products.html', products=products)
    
    except Exception as e:
        logging.error(f"Error loading user products: {e}")
        flash("Error loading your products. Please try again later.", "danger")
        return redirect(url_for('dashboard.analytics'))

@ecommerce_bp.route('/add-product', methods=['GET', 'POST'])
@login_required
def add_product():
    """Add new product form and handler"""
    if request.method == 'POST':
        try:
            # Get product details from form
            name = request.form.get('name')
            description = request.form.get('description')
            price = float(request.form.get('price', 0))
            category = request.form.get('category')
            
            # Create new product
            product = Product(
                user_id=current_user.id,
                name=name,
                description=description,
                price=price,
                category=category,
                images=[],
                in_stock=True
            )
            
            # Save product to get ID
            product_id = product.save()
            
            if not product_id:
                flash("Failed to add product. Please try again later.", "danger")
                return redirect(url_for('ecommerce.my_products'))
                
            flash("Product added successfully!", "success")
            return redirect(url_for('ecommerce.edit_product', product_id=product_id))
            
        except Exception as e:
            logging.error(f"Error adding product: {e}")
            flash(f"An error occurred: {str(e)}", "danger")
            
    return render_template('ecommerce/add_product.html')

@ecommerce_bp.route('/edit-product/<product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    """Edit product form and handler"""
    product = Product.get(product_id)
    
    if not product:
        flash("Product not found.", "warning")
        return redirect(url_for('ecommerce.my_products'))
        
    # Check if current user owns the product
    if product.user_id != current_user.id:
        flash("You don't have permission to edit this product.", "danger")
        return redirect(url_for('ecommerce.my_products'))
        
    if request.method == 'POST':
        try:
            # Update product details
            product.name = request.form.get('name')
            product.description = request.form.get('description')
            product.price = float(request.form.get('price', 0))
            product.category = request.form.get('category')
            product.in_stock = 'in_stock' in request.form
            
            # Save updated product
            product.save()
            flash("Product updated successfully!", "success")
            
        except Exception as e:
            logging.error(f"Error updating product: {e}")
            flash(f"An error occurred: {str(e)}", "danger")
            
    return render_template('ecommerce/edit_product.html', product=product)

@ecommerce_bp.route('/delete-product/<product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    """Delete product handler"""
    product = Product.get(product_id)
    
    if not product:
        return jsonify({'success': False, 'message': 'Product not found.'}), 404
        
    # Check if current user owns the product
    if product.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'You don\'t have permission to delete this product.'}), 403
        
    try:
        # Delete product
        if product.delete():
            return jsonify({'success': True, 'message': 'Product deleted successfully!'}), 200
        else:
            return jsonify({'success': False, 'message': 'Failed to delete product.'}), 500
            
    except Exception as e:
        logging.error(f"Error deleting product: {e}")
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'}), 500

@ecommerce_bp.route('/upload-product-image/<product_id>', methods=['POST'])
@login_required
def upload_product_image(product_id):
    """Upload product image handler"""
    product = Product.get(product_id)
    
    if not product:
        return jsonify({'success': False, 'message': 'Product not found.'}), 404
        
    # Check if current user owns the product
    if product.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'You don\'t have permission to edit this product.'}), 403
        
    try:
        # Check if image was uploaded
        if 'image' not in request.files:
            return jsonify({'success': False, 'message': 'No image file uploaded.'}), 400
            
        image_file = request.files['image']
        
        if image_file.filename == '':
            return jsonify({'success': False, 'message': 'No image file selected.'}), 400
            
        # Check file type (allow only images)
        allowed_extensions = {'jpg', 'jpeg', 'png', 'gif'}
        if '.' not in image_file.filename or image_file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return jsonify({'success': False, 'message': 'Invalid file type. Only JPG, JPEG, PNG, and GIF files are allowed.'}), 400
            
        # Generate unique filename
        filename = f"{uuid.uuid4().hex}_{secure_filename(image_file.filename)}"
        file_path = f"products/{product_id}/{filename}"
        
        # Upload image to Firebase Storage if bucket is available
        if bucket:
            blob = bucket.blob(file_path)
            blob.upload_from_string(
                image_file.read(),
                content_type=image_file.content_type
            )
            
            # Make image publicly accessible
            blob.make_public()
            
            # Get public URL
            image_url = blob.public_url
        else:
            # For development without Firebase Storage
            # Save to a temporary URL (in a real app, we'd use local storage)
            image_url = f"https://placeholder.co/400x300?text={filename}"
            logging.warning("Firebase Storage not configured, using placeholder image")
        
        # Add image URL to product
        product.images.append(image_url)
        product.save()
        
        return jsonify({
            'success': True, 
            'message': 'Image uploaded successfully!',
            'image_url': image_url
        }), 200
            
    except Exception as e:
        logging.error(f"Error uploading product image: {e}")
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'}), 500

@ecommerce_bp.route('/remove-product-image/<product_id>', methods=['POST'])
@login_required
def remove_product_image(product_id):
    """Remove product image handler"""
    product = Product.get(product_id)
    
    if not product:
        return jsonify({'success': False, 'message': 'Product not found.'}), 404
        
    # Check if current user owns the product
    if product.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'You don\'t have permission to edit this product.'}), 403
        
    try:
        # Get image URL from request
        image_url = request.json.get('image_url')
        
        if not image_url:
            return jsonify({'success': False, 'message': 'No image URL provided.'}), 400
            
        # Remove image URL from product
        if image_url in product.images:
            product.images.remove(image_url)
            product.save()
            
            # Try to delete from Firebase Storage if possible
            try:
                if bucket and image_url.startswith('https://storage.googleapis.com'):
                    path = image_url.split('/', 4)[-1]
                    bucket.delete_blob(path)
            except Exception as e:
                logging.warning(f"Could not delete image from storage: {e}")
            
            return jsonify({'success': True, 'message': 'Image removed successfully!'}), 200
        else:
            return jsonify({'success': False, 'message': 'Image not found in product.'}), 404
            
    except Exception as e:
        logging.error(f"Error removing product image: {e}")
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'}), 500
