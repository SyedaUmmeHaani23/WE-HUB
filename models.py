from firebase_admin import firestore
from flask_login import UserMixin

class User(UserMixin):
    """User model for Firebase authentication"""
    
    def __init__(self, uid, email=None, display_name=None, photo_url=None, business_data=None):
        self.id = uid
        self.email = email
        self.display_name = display_name
        self.photo_url = photo_url
        self.business_data = business_data or {}
    
    @staticmethod
    def get(user_id):
        """Get user by ID from Firestore"""
        from app import db
        if not db:
            return None
            
        user_doc = db.collection('users').document(user_id).get()
        if not user_doc.exists:
            return None
            
        user_data = user_doc.to_dict()
        return User(
            uid=user_id,
            email=user_data.get('email'),
            display_name=user_data.get('display_name'),
            photo_url=user_data.get('photo_url'),
            business_data=user_data.get('business_data')
        )
    
    def save(self):
        """Save user data to Firestore"""
        from app import db
        if not db:
            return False
            
        user_data = {
            'email': self.email,
            'display_name': self.display_name,
            'photo_url': self.photo_url,
            'business_data': self.business_data,
            'updated_at': firestore.SERVER_TIMESTAMP
        }
        
        db.collection('users').document(self.id).set(user_data, merge=True)
        return True

class Product:
    """Product model for e-commerce functionality"""
    
    def __init__(self, product_id=None, user_id=None, name=None, description=None, 
                 price=None, category=None, images=None, in_stock=True):
        self.id = product_id
        self.user_id = user_id
        self.name = name
        self.description = description
        self.price = price
        self.category = category
        self.images = images or []
        self.in_stock = in_stock
    
    @staticmethod
    def get(product_id):
        """Get product by ID from Firestore"""
        from app import db
        if not db:
            return None
            
        product_doc = db.collection('products').document(product_id).get()
        if not product_doc.exists:
            return None
            
        product_data = product_doc.to_dict()
        return Product(
            product_id=product_id,
            user_id=product_data.get('user_id'),
            name=product_data.get('name'),
            description=product_data.get('description'),
            price=product_data.get('price'),
            category=product_data.get('category'),
            images=product_data.get('images', []),
            in_stock=product_data.get('in_stock', True)
        )
    
    @staticmethod
    def get_by_user(user_id):
        """Get all products by user ID from Firestore"""
        from app import db
        if not db:
            return []
            
        products = []
        product_docs = db.collection('products').where('user_id', '==', user_id).stream()
        
        for doc in product_docs:
            product_data = doc.to_dict()
            products.append(Product(
                product_id=doc.id,
                user_id=product_data.get('user_id'),
                name=product_data.get('name'),
                description=product_data.get('description'),
                price=product_data.get('price'),
                category=product_data.get('category'),
                images=product_data.get('images', []),
                in_stock=product_data.get('in_stock', True)
            ))
        
        return products
    
    def save(self):
        """Save product data to Firestore"""
        from app import db
        if not db:
            return None
            
        product_data = {
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'images': self.images,
            'in_stock': self.in_stock,
            'updated_at': firestore.SERVER_TIMESTAMP
        }
        
        if self.id:
            db.collection('products').document(self.id).set(product_data, merge=True)
            return self.id
        else:
            doc_ref = db.collection('products').add(product_data)
            self.id = doc_ref[1].id
            return self.id
    
    def delete(self):
        """Delete product from Firestore"""
        from app import db
        if not db or not self.id:
            return False
            
        db.collection('products').document(self.id).delete()
        return True

class ForumPost:
    """Forum post model for community features"""
    
    def __init__(self, post_id=None, user_id=None, title=None, content=None, 
                 category=None, created_at=None, updated_at=None, comments=None):
        self.id = post_id
        self.user_id = user_id
        self.title = title
        self.content = content
        self.category = category
        self.created_at = created_at
        self.updated_at = updated_at
        self.comments = comments or []
    
    @staticmethod
    def get(post_id):
        """Get forum post by ID from Firestore"""
        from app import db
        if not db:
            return None
            
        post_doc = db.collection('forum_posts').document(post_id).get()
        if not post_doc.exists:
            return None
            
        post_data = post_doc.to_dict()
        return ForumPost(
            post_id=post_id,
            user_id=post_data.get('user_id'),
            title=post_data.get('title'),
            content=post_data.get('content'),
            category=post_data.get('category'),
            created_at=post_data.get('created_at'),
            updated_at=post_data.get('updated_at'),
            comments=post_data.get('comments', [])
        )
    
    def save(self):
        """Save forum post data to Firestore"""
        from app import db
        if not db:
            return None
            
        post_data = {
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'comments': self.comments,
            'updated_at': firestore.SERVER_TIMESTAMP
        }
        
        if not self.created_at:
            post_data['created_at'] = firestore.SERVER_TIMESTAMP
        
        if self.id:
            db.collection('forum_posts').document(self.id).set(post_data, merge=True)
            return self.id
        else:
            doc_ref = db.collection('forum_posts').add(post_data)
            self.id = doc_ref[1].id
            return self.id

class Event:
    """Event model for community events"""
    
    def __init__(self, event_id=None, user_id=None, title=None, description=None, 
                 date=None, time=None, location=None, is_virtual=False, meeting_link=None):
        self.id = event_id
        self.user_id = user_id
        self.title = title
        self.description = description
        self.date = date
        self.time = time
        self.location = location
        self.is_virtual = is_virtual
        self.meeting_link = meeting_link
    
    @staticmethod
    def get(event_id):
        """Get event by ID from Firestore"""
        from app import db
        if not db:
            return None
            
        event_doc = db.collection('events').document(event_id).get()
        if not event_doc.exists:
            return None
            
        event_data = event_doc.to_dict()
        return Event(
            event_id=event_id,
            user_id=event_data.get('user_id'),
            title=event_data.get('title'),
            description=event_data.get('description'),
            date=event_data.get('date'),
            time=event_data.get('time'),
            location=event_data.get('location'),
            is_virtual=event_data.get('is_virtual', False),
            meeting_link=event_data.get('meeting_link')
        )
    
    def save(self):
        """Save event data to Firestore"""
        from app import db
        if not db:
            return None
            
        event_data = {
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'date': self.date,
            'time': self.time,
            'location': self.location,
            'is_virtual': self.is_virtual,
            'meeting_link': self.meeting_link,
            'updated_at': firestore.SERVER_TIMESTAMP
        }
        
        if self.id:
            db.collection('events').document(self.id).set(event_data, merge=True)
            return self.id
        else:
            doc_ref = db.collection('events').add(event_data)
            self.id = doc_ref[1].id
            return self.id
