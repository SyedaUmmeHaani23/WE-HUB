"""
Events routes for Women Entrepreneurs Hub.
Handles events, workshops, and event registrations.
"""
import logging
import os
from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from app import db, firestore_db
from models import User, Event, EventRegistration
import firebase_admin
from datetime import datetime

bp = Blueprint('events', __name__, url_prefix='/events')

@bp.route('/', methods=['GET'])
def index():
    """Render the events page with listings."""
    # Check if user is logged in
    user_data = session.get('user_data')
    
    # Get Google Maps API key from environment
    google_maps_api_key = os.environ.get('GOOGLE_MAPS_API_KEY', '')
    
    return render_template(
        'events.html',
        user_data=user_data,
        google_maps_api_key=google_maps_api_key
    )

@bp.route('/<event_id>', methods=['GET'])
def view_event(event_id):
    """View a single event."""
    # Check if user is logged in
    user_data = session.get('user_data')
    
    try:
        # If it's a Firebase ID, get the event from Firestore
        if firestore_db and not event_id.isdigit():
            event_doc = firestore_db.collection('events').document(event_id).get()
            if not event_doc.exists:
                return redirect(url_for('events.index'))
            
            event_data = event_doc.to_dict()
            
            # Check if user is registered
            is_registered = False
            if user_data:
                # Check in Firestore for registration
                registrations_query = firestore_db.collection('event_registrations').where(
                    'event_id', '==', event_id
                ).where(
                    'user_id', '==', user_data.get('firebase_uid')
                ).limit(1).get()
                
                is_registered = len(registrations_query) > 0
            
            # Get Google Maps API key from environment
            google_maps_api_key = os.environ.get('GOOGLE_MAPS_API_KEY', '')
            
            return render_template(
                'event-details.html',
                event=event_data,
                event_id=event_id,
                user_data=user_data,
                is_registered=is_registered,
                is_firestore=True,
                google_maps_api_key=google_maps_api_key
            )
        else:
            # Get event from database
            event = Event.query.get_or_404(event_id)
            
            # Check if user is registered
            is_registered = False
            if user_data:
                registration = EventRegistration.query.filter_by(
                    event_id=event.id,
                    user_id=user_data.get('id')
                ).first()
                
                is_registered = registration is not None
            
            # Get Google Maps API key from environment
            google_maps_api_key = os.environ.get('GOOGLE_MAPS_API_KEY', '')
            
            return render_template(
                'event-details.html',
                event=event,
                user_data=user_data,
                is_registered=is_registered,
                is_firestore=False,
                google_maps_api_key=google_maps_api_key
            )
    
    except Exception as e:
        logging.error(f"Error viewing event {event_id}: {e}")
        return redirect(url_for('events.index'))

@bp.route('/create', methods=['GET'])
def create_event_form():
    """Render the create event form."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return redirect(url_for('auth.login'))
    
    return render_template(
        'create-event.html',
        user_data=user_data
    )

@bp.route('/api/events', methods=['POST'])
def create_event():
    """Create a new event."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        # Get JSON data
        data = request.json
        
        # Validate required fields
        required_fields = ['title', 'start_datetime', 'end_datetime']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        
        # Get user ID
        user_id = user_data.get('id')
        
        # Parse dates
        try:
            start_datetime = datetime.fromisoformat(data.get('start_datetime').replace('Z', '+00:00'))
            end_datetime = datetime.fromisoformat(data.get('end_datetime').replace('Z', '+00:00'))
        except (ValueError, TypeError):
            # Handle Firestore timestamps
            if hasattr(data.get('start_datetime'), 'seconds'):
                start_datetime = datetime.fromtimestamp(data.get('start_datetime').seconds)
                end_datetime = datetime.fromtimestamp(data.get('end_datetime').seconds)
            else:
                return jsonify({'success': False, 'message': 'Invalid datetime format'}), 400
        
        # Create new event
        event = Event(
            user_id=user_id,
            firebase_id=data.get('firebase_id'),
            title=data.get('title'),
            description=data.get('description', ''),
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            location=data.get('location'),
            virtual_link=data.get('virtual_link'),
            is_virtual=data.get('is_virtual', False),
            max_participants=data.get('max_participants'),
            image_url=data.get('image_url'),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Add to database
        db.session.add(event)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Event created successfully',
            'event_id': event.id
        })
    
    except Exception as e:
        logging.error(f"Error creating event: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/events/register', methods=['POST'])
def register_for_event():
    """Register for an event."""
    # Check if user is logged in
    user_data = session.get('user_data')
    if not user_data:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    try:
        # Get JSON data
        data = request.json
        
        # Validate required fields
        if 'event_id' not in data:
            return jsonify({'success': False, 'message': 'Missing event_id'}), 400
        
        # Get user ID
        user_id = user_data.get('id')
        event_id = data.get('event_id')
        
        # Check if this is a Firebase event ID
        if firestore_db and not event_id.isdigit():
            # Check if already registered
            registrations_query = firestore_db.collection('event_registrations').where(
                'event_id', '==', event_id
            ).where(
                'user_id', '==', user_data.get('firebase_uid')
            ).limit(1).get()
            
            if len(registrations_query) > 0:
                return jsonify({'success': False, 'message': 'Already registered for this event'}), 400
            
            # Create registration in Firestore
            registration_data = {
                'event_id': event_id,
                'user_id': user_data.get('firebase_uid'),
                'registration_date': firebase_admin.firestore.SERVER_TIMESTAMP,
                'status': 'registered'
            }
            
            if 'firebase_id' in data:
                registration_ref = firestore_db.collection('event_registrations').document(data.get('firebase_id'))
                registration_ref.set(registration_data)
                registration_id = data.get('firebase_id')
            else:
                registration_ref = firestore_db.collection('event_registrations').add(registration_data)
                registration_id = registration_ref[1].id
            
            return jsonify({
                'success': True,
                'message': 'Registration successful',
                'registration_id': registration_id
            })
        else:
            # Check if event exists
            event = Event.query.get(event_id)
            if not event:
                return jsonify({'success': False, 'message': 'Event not found'}), 404
            
            # Check if already registered
            existing_registration = EventRegistration.query.filter_by(
                event_id=event_id,
                user_id=user_id
            ).first()
            
            if existing_registration:
                return jsonify({'success': False, 'message': 'Already registered for this event'}), 400
            
            # Create new registration
            registration = EventRegistration(
                event_id=event_id,
                user_id=user_id,
                firebase_id=data.get('firebase_id'),
                registration_date=datetime.utcnow(),
                status='registered'
            )
            
            # Add to database
            db.session.add(registration)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Registration successful',
                'registration_id': registration.id
            })
    
    except Exception as e:
        logging.error(f"Error registering for event: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/events/upcoming', methods=['GET'])
def get_upcoming_events():
    """Get upcoming events."""
    try:
        # Get limit parameter, default to 10
        limit = request.args.get('limit', 10, type=int)
        
        # Get upcoming events from database
        now = datetime.utcnow()
        events = Event.query.filter(
            Event.start_datetime > now
        ).order_by(
            Event.start_datetime.asc()
        ).limit(limit).all()
        
        # Format events for JSON response
        events_data = []
        for event in events:
            events_data.append({
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'start_datetime': event.start_datetime.isoformat(),
                'end_datetime': event.end_datetime.isoformat(),
                'location': event.location,
                'is_virtual': event.is_virtual,
                'image_url': event.image_url
            })
        
        return jsonify(events_data)
    
    except Exception as e:
        logging.error(f"Error getting upcoming events: {e}")
        return jsonify([]), 500

@bp.route('/api/events/past', methods=['GET'])
def get_past_events():
    """Get past events."""
    try:
        # Get limit parameter, default to 10
        limit = request.args.get('limit', 10, type=int)
        
        # Get past events from database
        now = datetime.utcnow()
        events = Event.query.filter(
            Event.end_datetime < now
        ).order_by(
            Event.end_datetime.desc()
        ).limit(limit).all()
        
        # Format events for JSON response
        events_data = []
        for event in events:
            events_data.append({
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'start_datetime': event.start_datetime.isoformat(),
                'end_datetime': event.end_datetime.isoformat(),
                'location': event.location,
                'is_virtual': event.is_virtual,
                'image_url': event.image_url
            })
        
        return jsonify(events_data)
    
    except Exception as e:
        logging.error(f"Error getting past events: {e}")
        return jsonify([]), 500
