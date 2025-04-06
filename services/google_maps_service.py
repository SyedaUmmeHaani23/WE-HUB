"""
Google Maps service for Women Entrepreneurs Hub.
Provides functions for interacting with Google Maps API.
"""
import logging
import os
import json
import requests
from models import User
from app import db

def get_nearby_businesses(latitude, longitude, radius=5000, limit=10):
    """
    Get nearby women-owned businesses.
    
    Args:
        latitude (float): The latitude of the center point.
        longitude (float): The longitude of the center point.
        radius (int): The radius in meters to search within.
        limit (int): The maximum number of businesses to return.
        
    Returns:
        list: A list of nearby businesses.
    """
    try:
        # In a real implementation, this would use the Google Places API
        # For now, get users with location data within the app database
        
        # Get all users with location data
        users = User.query.filter(
            User.latitude.isnot(None),
            User.longitude.isnot(None),
            User.business_name.isnot(None)
        ).limit(limit).all()
        
        # Format business data
        businesses = []
        for user in users:
            businesses.append({
                'id': user.id,
                'name': user.business_name,
                'description': user.business_description,
                'category': user.business_category,
                'latitude': user.latitude,
                'longitude': user.longitude,
                'address': user.address,
                'website': user.website,
                'phone': user.phone,
                'profile_picture': user.profile_picture
            })
        
        return businesses
    except Exception as e:
        logging.error(f"Error getting nearby businesses: {e}")
        return []

def get_business_info(firebase_uid):
    """
    Get business information from Google My Business.
    
    Args:
        firebase_uid (str): The Firebase UID of the user.
        
    Returns:
        dict: A dictionary containing business information.
    """
    try:
        # In a real implementation, this would integrate with the Google My Business API
        # For now, return info from the user's profile
        from models import User
        
        # Get user by Firebase UID
        user = User.query.filter_by(firebase_uid=firebase_uid).first()
        
        if not user:
            return {
                'name': '',
                'address': '',
                'website': '',
                'phone': '',
                'business_hours': {},
                'reviews': []
            }
        
        return {
            'name': user.business_name or '',
            'address': user.address or '',
            'website': user.website or '',
            'phone': user.phone or '',
            'business_hours': {},  # Would come from Google My Business
            'reviews': []  # Would come from Google My Business
        }
    except Exception as e:
        logging.error(f"Error getting business info: {e}")
        return {
            'name': '',
            'address': '',
            'website': '',
            'phone': '',
            'business_hours': {},
            'reviews': []
        }