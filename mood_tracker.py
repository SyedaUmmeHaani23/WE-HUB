"""
Mood and productivity tracker for Women Entrepreneurs Hub.
Allows users to track their daily mood and productivity levels.
"""
import json
import calendar
import csv
import io
from datetime import datetime, date, timedelta
from functools import wraps

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, abort, make_response
from flask_login import login_required, current_user
from sqlalchemy import func

from app import db
from models import MoodTracker, MoodEmojiPreset, User

# Create Blueprint for mood tracker routes
mood_tracker_bp = Blueprint('mood_tracker', __name__, url_prefix='/mood-tracker')

# Default emoji presets
DEFAULT_MOOD_EMOJIS = [
    {"emoji": "😊", "label": "Happy", "value": 5},
    {"emoji": "😃", "label": "Excited", "value": 5},
    {"emoji": "😌", "label": "Content", "value": 4},
    {"emoji": "😐", "label": "Neutral", "value": 3},
    {"emoji": "😕", "label": "Confused", "value": 2},
    {"emoji": "😢", "label": "Sad", "value": 1},
    {"emoji": "😠", "label": "Angry", "value": 1},
    {"emoji": "😴", "label": "Tired", "value": 2}
]

DEFAULT_PRODUCTIVITY_EMOJIS = [
    {"emoji": "🚀", "label": "Super Productive", "value": 10},
    {"emoji": "⚡", "label": "Energetic", "value": 9},
    {"emoji": "💪", "label": "Strong", "value": 8},
    {"emoji": "👍", "label": "Good", "value": 7},
    {"emoji": "🙂", "label": "Average", "value": 5},
    {"emoji": "🐢", "label": "Slow", "value": 3},
    {"emoji": "😴", "label": "Sleepy", "value": 2},
    {"emoji": "🛑", "label": "Blocked", "value": 1}
]

def init_emoji_presets(user_id):
    """Initialize default emoji presets for a user."""
    # Check if user already has presets
    existing_presets = MoodEmojiPreset.query.filter_by(user_id=user_id).first()
    if existing_presets:
        return  # User already has presets

    # Create mood emoji presets
    for preset in DEFAULT_MOOD_EMOJIS:
        mood_preset = MoodEmojiPreset(
            user_id=user_id,
            category="mood",
            emoji=preset["emoji"],
            label=preset["label"],
            value=preset["value"],
            is_default=True
        )
        db.session.add(mood_preset)

    # Create productivity emoji presets
    for preset in DEFAULT_PRODUCTIVITY_EMOJIS:
        prod_preset = MoodEmojiPreset(
            user_id=user_id,
            category="productivity",
            emoji=preset["emoji"],
            label=preset["label"],
            value=preset["value"],
            is_default=True
        )
        db.session.add(prod_preset)

    db.session.commit()

def get_calendar_month(year, month, user_id):
    """Generate calendar data for the specified month."""
    # Get the first day of the month and the number of days
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    
    # Find the first day of the week for this month
    first_weekday = first_day.weekday()
    # Adjust for Sunday as the first day of the week (0-6, where 0 is Sunday)
    first_weekday = (first_weekday + 1) % 7
    
    # Get entries for this month
    entries = MoodTracker.query.filter_by(user_id=user_id).filter(
        MoodTracker.date.between(first_day, last_day)
    ).all()
    
    # Create a dictionary for quick lookup of entries by date
    entry_dict = {entry.date: entry for entry in entries}
    
    # Generate calendar weeks
    calendar_weeks = []
    current_week = [{"date": None, "entry": None} for _ in range(first_weekday)]
    
    for day in range(1, calendar.monthrange(year, month)[1] + 1):
        current_date = date(year, month, day)
        entry = entry_dict.get(current_date)
        
        current_week.append({"date": current_date, "entry": entry})
        
        if len(current_week) == 7:
            calendar_weeks.append(current_week)
            current_week = []
    
    # Fill the last week with None values if needed
    if current_week:
        current_week.extend([{"date": None, "entry": None} for _ in range(7 - len(current_week))])
        calendar_weeks.append(current_week)
    
    return calendar_weeks

@mood_tracker_bp.route('/')
@login_required
def index():
    """Render the mood tracker dashboard."""
    # Initialize emoji presets if needed
    init_emoji_presets(current_user.id)
    
    # Get today's date and determine which month to display
    today = date.today()
    year = request.args.get('year', today.year, type=int)
    month = request.args.get('month', today.month, type=int)
    
    # Generate calendar data
    calendar_weeks = get_calendar_month(year, month, current_user.id)
    current_month = f"{calendar.month_name[month]} {year}"
    
    # Get recent entries
    recent_entries = MoodTracker.query.filter_by(
        user_id=current_user.id
    ).order_by(MoodTracker.date.desc()).limit(5).all()
    
    # Get user's emoji presets
    mood_presets = MoodEmojiPreset.query.filter_by(
        user_id=current_user.id,
        category="mood"
    ).all()
    
    productivity_presets = MoodEmojiPreset.query.filter_by(
        user_id=current_user.id,
        category="productivity"
    ).all()
    
    # Check if user has already tracked mood for today
    today_entry = MoodTracker.query.filter_by(
        user_id=current_user.id,
        date=today
    ).first()
    
    # Calculate some basic stats
    entries_this_month = MoodTracker.query.filter_by(
        user_id=current_user.id
    ).filter(
        MoodTracker.date.between(
            date(year, month, 1),
            date(year, month, calendar.monthrange(year, month)[1])
        )
    ).all()
    
    stats = {
        "average_productivity": 0,
        "most_common_mood_emoji": "😐"
    }
    
    if entries_this_month:
        # Calculate average productivity
        total_productivity = sum(entry.productivity_level for entry in entries_this_month)
        stats["average_productivity"] = total_productivity / len(entries_this_month)
        
        # Find most common mood emoji
        mood_counts = {}
        for entry in entries_this_month:
            mood_counts[entry.mood_emoji] = mood_counts.get(entry.mood_emoji, 0) + 1
        
        if mood_counts:
            stats["most_common_mood_emoji"] = max(mood_counts.items(), key=lambda x: x[1])[0]
    
    return render_template(
        'mood_tracker/index.html',
        title="Mood & Productivity Tracker",
        calendar_weeks=calendar_weeks,
        current_month=current_month,
        recent_entries=recent_entries,
        mood_presets=mood_presets,
        productivity_presets=productivity_presets,
        today_entry=today_entry,
        today=today,
        stats=stats
    )

@mood_tracker_bp.route('/log', methods=['GET', 'POST'])
@login_required
def log_mood():
    """Log mood and productivity for today."""
    if request.method == 'POST':
        # Get date from form or use today's date
        date_str = request.form.get('date')
        if date_str:
            try:
                entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                entry_date = date.today()
        else:
            entry_date = date.today()
        
        # Check if already logged for this date
        existing_entry = MoodTracker.query.filter_by(
            user_id=current_user.id,
            date=entry_date
        ).first()
        
        # Get mood emoji (either from preset or custom)
        mood_emoji = request.form.get('mood_emoji')
        if mood_emoji == 'custom':
            mood_emoji = request.form.get('custom_mood_emoji', '😐')
            mood_label = request.form.get('custom_mood_label', '')
        else:
            # Get label from preset
            preset = MoodEmojiPreset.query.filter_by(
                user_id=current_user.id,
                category='mood',
                emoji=mood_emoji
            ).first()
            mood_label = preset.label if preset else ''
        
        productivity_level = int(request.form.get('productivity_level', 5))
        
        # Get productivity emoji based on level
        productivity_preset = MoodEmojiPreset.query.filter_by(
            user_id=current_user.id,
            category='productivity',
            value=productivity_level
        ).first()
        productivity_emoji = productivity_preset.emoji if productivity_preset else '📊'
        
        notes = request.form.get('notes', '')
        
        if existing_entry:
            # Update existing entry
            existing_entry.mood_emoji = mood_emoji
            existing_entry.mood_label = mood_label
            existing_entry.productivity_level = productivity_level
            existing_entry.productivity_emoji = productivity_emoji
            existing_entry.notes = notes
            existing_entry.updated_at = datetime.utcnow()
            db.session.commit()
            flash('Your mood and productivity have been updated!', 'success')
        else:
            # Create new entry
            new_entry = MoodTracker(
                user_id=current_user.id,
                date=entry_date,
                mood_emoji=mood_emoji,
                mood_label=mood_label,
                productivity_level=productivity_level,
                productivity_emoji=productivity_emoji,
                notes=notes
            )
            db.session.add(new_entry)
            db.session.commit()
            flash('Your mood and productivity have been logged!', 'success')
        
        return redirect(url_for('mood_tracker.index'))
    
    # GET request - render form
    init_emoji_presets(current_user.id)
    
    # Get date from query params or use today
    date_str = request.args.get('date')
    if date_str:
        try:
            entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            entry_date = date.today()
            date_str = None
    else:
        entry_date = date.today()
        date_str = None
        
    # Get presets
    mood_presets = MoodEmojiPreset.query.filter_by(
        user_id=current_user.id,
        category="mood"
    ).all()
    
    mood_presets_emojis = [preset.emoji for preset in mood_presets]
    
    productivity_presets = MoodEmojiPreset.query.filter_by(
        user_id=current_user.id,
        category="productivity"
    ).all()
    
    # Check if user has already tracked mood for this date
    entry = MoodTracker.query.filter_by(
        user_id=current_user.id,
        date=entry_date
    ).first()
    
    return render_template(
        'mood_tracker/log_entry.html',
        title="Log Your Mood & Productivity",
        mood_presets=mood_presets,
        mood_presets_emojis=mood_presets_emojis,
        productivity_presets=productivity_presets,
        entry=entry,
        date_str=date_str,
        entry_id=entry.id if entry else None
    )

@mood_tracker_bp.route('/edit/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def edit_entry(entry_id):
    """Edit a mood tracker entry."""
    entry = MoodTracker.query.get_or_404(entry_id)
    
    # Check if the entry belongs to the current user
    if entry.user_id != current_user.id:
        abort(403)
    
    if request.method == 'POST':
        # Get mood emoji (either from preset or custom)
        mood_emoji = request.form.get('mood_emoji')
        if mood_emoji == 'custom':
            mood_emoji = request.form.get('custom_mood_emoji', '😐')
            mood_label = request.form.get('custom_mood_label', '')
        else:
            # Get label from preset
            preset = MoodEmojiPreset.query.filter_by(
                user_id=current_user.id,
                category='mood',
                emoji=mood_emoji
            ).first()
            mood_label = preset.label if preset else ''
        
        # Update entry from form data
        entry.mood_emoji = mood_emoji
        entry.mood_label = mood_label
        entry.productivity_level = int(request.form.get('productivity_level', 5))
        
        # Get productivity emoji based on level
        productivity_preset = MoodEmojiPreset.query.filter_by(
            user_id=current_user.id,
            category='productivity',
            value=entry.productivity_level
        ).first()
        entry.productivity_emoji = productivity_preset.emoji if productivity_preset else '📊'
        
        entry.notes = request.form.get('notes', '')
        entry.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Entry updated successfully!', 'success')
        return redirect(url_for('mood_tracker.index'))
    
    # GET request - render form with existing data
    mood_presets = MoodEmojiPreset.query.filter_by(
        user_id=current_user.id,
        category="mood"
    ).all()
    
    mood_presets_emojis = [preset.emoji for preset in mood_presets]
    
    productivity_presets = MoodEmojiPreset.query.filter_by(
        user_id=current_user.id,
        category="productivity"
    ).all()
    
    return render_template(
        'mood_tracker/log_entry.html',
        title="Edit Mood & Productivity Entry",
        entry=entry,
        mood_presets=mood_presets,
        mood_presets_emojis=mood_presets_emojis,
        productivity_presets=productivity_presets,
        entry_id=entry_id
    )

@mood_tracker_bp.route('/delete/<int:entry_id>', methods=['POST'])
@login_required
def delete_entry(entry_id):
    """Delete a mood tracker entry."""
    entry = MoodTracker.query.get_or_404(entry_id)
    
    # Check if the entry belongs to the current user
    if entry.user_id != current_user.id:
        abort(403)
    
    db.session.delete(entry)
    db.session.commit()
    
    flash('Entry deleted successfully!', 'success')
    return redirect(url_for('mood_tracker.index'))

@mood_tracker_bp.route('/emoji-presets', methods=['GET', 'POST'])
@login_required
def manage_presets():
    """Manage emoji presets for mood and productivity."""
    if request.method == 'POST':
        category = request.form.get('category')
        emoji = request.form.get('emoji')
        label = request.form.get('label')
        value = int(request.form.get('value', 5))
        
        # Create new preset
        new_preset = MoodEmojiPreset(
            user_id=current_user.id,
            category=category,
            emoji=emoji,
            label=label,
            value=value,
            is_default=False
        )
        
        db.session.add(new_preset)
        db.session.commit()
        
        flash(f'New {category} emoji preset added!', 'success')
        return redirect(url_for('mood_tracker.manage_presets'))
    
    # GET request - show preset management page
    mood_presets = MoodEmojiPreset.query.filter_by(
        user_id=current_user.id,
        category="mood"
    ).all()
    
    productivity_presets = MoodEmojiPreset.query.filter_by(
        user_id=current_user.id,
        category="productivity"
    ).all()
    
    return render_template(
        'mood_tracker/manage_presets.html',
        title="Manage Emoji Presets",
        mood_presets=mood_presets,
        productivity_presets=productivity_presets
    )

@mood_tracker_bp.route('/emoji-presets/delete/<int:preset_id>', methods=['POST'])
@login_required
def delete_preset(preset_id):
    """Delete an emoji preset."""
    preset = MoodEmojiPreset.query.get_or_404(preset_id)
    
    # Check if the preset belongs to the current user
    if preset.user_id != current_user.id:
        abort(403)
    
    # Don't allow deletion of default presets
    if preset.is_default:
        flash('Default presets cannot be deleted.', 'warning')
        return redirect(url_for('mood_tracker.manage_presets'))
    
    db.session.delete(preset)
    db.session.commit()
    
    flash('Preset deleted successfully!', 'success')
    return redirect(url_for('mood_tracker.manage_presets'))

@mood_tracker_bp.route('/analytics')
@login_required
def analytics():
    """View mood and productivity analytics."""
    # Get date range from request args or default to last 30 days
    today = date.today()
    default_start = today - timedelta(days=30)
    
    try:
        start_date = datetime.strptime(request.args.get('start_date', ''), '%Y-%m-%d').date()
    except (ValueError, TypeError):
        start_date = default_start
    
    try:
        end_date = datetime.strptime(request.args.get('end_date', ''), '%Y-%m-%d').date()
    except (ValueError, TypeError):
        end_date = today
    
    # Get entries within the date range
    entries = MoodTracker.query.filter_by(user_id=current_user.id).filter(
        MoodTracker.date.between(start_date, end_date)
    ).order_by(MoodTracker.date.asc()).all()
    
    # Calculate total days in range
    days_in_range = (end_date - start_date).days + 1
    tracking_percentage = (len(entries) / days_in_range * 100) if days_in_range > 0 else 0
    
    # Prepare chart data
    dates = [entry.date.strftime('%Y-%m-%d') for entry in entries]
    productivity_levels = [entry.productivity_level for entry in entries]
    
    # Prepare data for mood distribution chart
    mood_count = {}
    for entry in entries:
        if entry.mood_emoji in mood_count:
            mood_count[entry.mood_emoji]['count'] += 1
        else:
            label = entry.mood_label or "Unlabeled"
            mood_count[entry.mood_emoji] = {
                'count': 1, 
                'label': label
            }
    
    mood_distribution_labels = [f"{data['label']} {emoji}" for emoji, data in mood_count.items()]
    mood_distribution_data = [data['count'] for _, data in mood_count.items()]
    
    # Prepare data for productivity trend chart
    productivity_trend_labels = [entry.date.strftime('%m/%d') for entry in entries]
    productivity_trend_data = productivity_levels
    
    # Prepare data for weekday analysis
    weekday_productivity = [0] * 7
    weekday_counts = [0] * 7
    weekday_positive_mood_counts = [0] * 7
    
    for entry in entries:
        weekday = entry.date.weekday()
        weekday_productivity[weekday] += entry.productivity_level
        weekday_counts[weekday] += 1
        
        # Get mood value from preset
        mood_preset = MoodEmojiPreset.query.filter_by(
            user_id=current_user.id,
            category="mood",
            emoji=entry.mood_emoji
        ).first()
        
        # Count positive moods (value > 3)
        if mood_preset and mood_preset.value > 3:
            weekday_positive_mood_counts[weekday] += 1
    
    # Calculate averages
    weekday_productivity_data = [
        round(weekday_productivity[i] / weekday_counts[i], 1) if weekday_counts[i] > 0 else 0
        for i in range(7)
    ]
    
    weekday_mood_data = [
        round(weekday_positive_mood_counts[i] / weekday_counts[i] * 100, 1) if weekday_counts[i] > 0 else 0
        for i in range(7)
    ]
    
    # Prepare correlation data
    correlation_data = []
    for entry in entries:
        mood_preset = MoodEmojiPreset.query.filter_by(
            user_id=current_user.id,
            category="mood",
            emoji=entry.mood_emoji
        ).first()
        
        mood_value = mood_preset.value if mood_preset else 3
        
        correlation_data.append({
            'x': mood_value,
            'y': entry.productivity_level,
            'date': entry.date.strftime('%Y-%m-%d')
        })
    
    # Calculate stats
    avg_productivity = sum(productivity_levels) / len(productivity_levels) if productivity_levels else 0
    
    # Find most common mood
    most_common_mood = {'emoji': '😐', 'label': 'Neutral', 'percentage': 0}
    if mood_count:
        max_count_emoji = max(mood_count.items(), key=lambda x: x[1]['count'])[0]
        max_count = mood_count[max_count_emoji]['count']
        percentage = (max_count / len(entries) * 100) if entries else 0
        
        most_common_mood = {
            'emoji': max_count_emoji,
            'label': mood_count[max_count_emoji]['label'],
            'percentage': percentage
        }
    
    # Find top productivity day of week
    top_productivity_day = {'name': 'N/A', 'avg': 0}
    if any(weekday_productivity_data):
        max_index = weekday_productivity_data.index(max(weekday_productivity_data))
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        top_productivity_day = {
            'name': day_names[max_index],
            'avg': weekday_productivity_data[max_index]
        }
    
    # Generate insights
    insights = generate_insights(entries, weekday_productivity_data, most_common_mood, correlation_data)
    
    return render_template(
        'mood_tracker/analytics.html',
        title="Mood & Productivity Analytics",
        entries=entries,
        start_date=start_date,
        end_date=end_date,
        total_entries=len(entries),
        tracking_percentage=tracking_percentage,
        mood_distribution_labels=json.dumps(mood_distribution_labels),
        mood_distribution_data=json.dumps(mood_distribution_data),
        productivity_trend_labels=json.dumps(productivity_trend_labels),
        productivity_trend_data=json.dumps(productivity_trend_data),
        weekday_productivity_data=json.dumps(weekday_productivity_data),
        weekday_mood_data=json.dumps(weekday_mood_data),
        correlation_data=json.dumps(correlation_data),
        most_common_mood=most_common_mood,
        avg_productivity=avg_productivity,
        top_productivity_day=top_productivity_day,
        insights=insights
    )

def generate_insights(entries, weekday_productivity, most_common_mood, correlation_data):
    """Generate insights based on mood and productivity data."""
    insights = []
    
    if not entries or len(entries) < 5:
        return []
    
    # Calculate trend over time
    if len(entries) >= 7:
        first_week = entries[:7]
        last_week = entries[-7:]
        
        first_week_prod = sum(e.productivity_level for e in first_week) / len(first_week)
        last_week_prod = sum(e.productivity_level for e in last_week) / len(last_week)
        
        prod_change = last_week_prod - first_week_prod
        
        if abs(prod_change) >= 1:
            trend_insight = {
                'icon': '📈' if prod_change > 0 else '📉',
                'title': 'Productivity Trend',
                'description': f"Your productivity has {'increased' if prod_change > 0 else 'decreased'} by {abs(prod_change):.1f} points on average compared to the beginning of this period.",
                'recommendation': "Keep up the good work!" if prod_change > 0 else "Consider what factors might be affecting your productivity and make adjustments to your routine."
            }
            insights.append(trend_insight)
    
    # Weekday patterns
    if any(weekday_productivity):
        max_day_index = weekday_productivity.index(max(weekday_productivity))
        min_day_index = weekday_productivity.index(min(filter(lambda x: x > 0, weekday_productivity)))
        
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        weekday_insight = {
            'icon': '📆',
            'title': 'Weekday Patterns',
            'description': f"You're most productive on {day_names[max_day_index]}s and least productive on {day_names[min_day_index]}s.",
            'recommendation': f"Consider scheduling your most important tasks on {day_names[max_day_index]}s when you tend to be most productive."
        }
        insights.append(weekday_insight)
    
    # Mood-productivity correlation
    if correlation_data and len(correlation_data) >= 5:
        # Simple correlation calculation
        mood_values = [d['x'] for d in correlation_data]
        prod_values = [d['y'] for d in correlation_data]
        
        mood_mean = sum(mood_values) / len(mood_values)
        prod_mean = sum(prod_values) / len(prod_values)
        
        numerator = sum((mood_values[i] - mood_mean) * (prod_values[i] - prod_mean) for i in range(len(correlation_data)))
        mood_variance = sum((x - mood_mean) ** 2 for x in mood_values)
        prod_variance = sum((y - prod_mean) ** 2 for y in prod_values)
        
        correlation = numerator / ((mood_variance * prod_variance) ** 0.5) if mood_variance * prod_variance > 0 else 0
        
        if abs(correlation) > 0.5:
            relation = "strong positive" if correlation > 0.7 else "positive" if correlation > 0 else "negative"
            
            correlation_insight = {
                'icon': '🔄',
                'title': 'Mood-Productivity Connection',
                'description': f"There appears to be a {relation} correlation between your mood and productivity levels.",
                'recommendation': "Focus on activities that boost your mood, as they're likely to increase your productivity as well." if correlation > 0 else "Your productivity seems less dependent on your mood. Focus on establishing productive routines regardless of how you feel."
            }
            insights.append(correlation_insight)
    
    # Most common mood insight
    if most_common_mood and most_common_mood['percentage'] > 30:
        mood_insight = {
            'icon': most_common_mood['emoji'],
            'title': 'Dominant Mood',
            'description': f"You reported feeling '{most_common_mood['label']}' ({most_common_mood['emoji']}) for {most_common_mood['percentage']:.0f}% of the tracked days.",
            'recommendation': None
        }
        insights.append(mood_insight)
    
    # Consistency insight
    days_tracked = len(entries)
    days_in_range = (entries[-1].date - entries[0].date).days + 1 if entries else 0
    tracking_rate = days_tracked / days_in_range if days_in_range > 0 else 0
    
    if tracking_rate < 0.7 and days_in_range >= 14:
        consistency_insight = {
            'icon': '📝',
            'title': 'Tracking Consistency',
            'description': f"You've tracked your mood for {days_tracked} out of {days_in_range} days ({tracking_rate*100:.0f}%).",
            'recommendation': "More consistent tracking will provide better insights. Try setting a daily reminder to log your mood."
        }
        insights.append(consistency_insight)
    
    return insights[:4]  # Limit to 4 most relevant insights

@mood_tracker_bp.route('/emoji-presets/add', methods=['POST'])
@login_required
def add_preset():
    """Add a new emoji preset."""
    if request.method == 'POST':
        category = request.form.get('category')
        emoji = request.form.get('emoji')
        label = request.form.get('label')
        value = request.form.get('value')
        
        if not emoji or not label or not category:
            flash('Emoji, label, and category are required.', 'error')
            return redirect(url_for('mood_tracker.manage_presets'))
        
        # Create new preset
        new_preset = MoodEmojiPreset(
            user_id=current_user.id,
            category=category,
            emoji=emoji,
            label=label,
            value=int(value) if value and category == 'productivity' else None,
            is_default=False
        )
        
        db.session.add(new_preset)
        db.session.commit()
        
        flash(f'New {category} emoji preset added successfully!', 'success')
        return redirect(url_for('mood_tracker.manage_presets'))

@mood_tracker_bp.route('/emoji-presets/save', methods=['POST'])
@login_required
def save_preset():
    """Save a new emoji preset from AJAX request."""
    if request.method == 'POST':
        try:
            data = request.get_json()
            category = data.get('category')
            emoji = data.get('emoji')
            label = data.get('label')
            value = data.get('value')
            
            if not emoji or not label or not category:
                return jsonify({'success': False, 'error': 'Emoji, label, and category are required.'})
            
            # Create new preset
            new_preset = MoodEmojiPreset(
                user_id=current_user.id,
                category=category,
                emoji=emoji,
                label=label,
                value=int(value) if value and category == 'productivity' else None,
                is_default=False
            )
            
            db.session.add(new_preset)
            db.session.commit()
            
            return jsonify({'success': True})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

@mood_tracker_bp.route('/emoji-presets/reset', methods=['POST'])
@login_required
def reset_presets():
    """Reset emoji presets to default values."""
    if request.method == 'POST':
        # Delete all custom presets (non-default ones)
        custom_presets = MoodEmojiPreset.query.filter_by(
            user_id=current_user.id,
            is_default=False
        ).all()
        
        for preset in custom_presets:
            db.session.delete(preset)
        
        # Delete all default presets
        default_presets = MoodEmojiPreset.query.filter_by(
            user_id=current_user.id,
            is_default=True
        ).all()
        
        for preset in default_presets:
            db.session.delete(preset)
        
        db.session.commit()
        
        # Reinitialize default presets
        init_emoji_presets(current_user.id)
        
        flash('Emoji presets have been reset to default values.', 'success')
        return redirect(url_for('mood_tracker.manage_presets'))

@mood_tracker_bp.route('/export/data')
@login_required
def export_data():
    """Export mood and productivity data."""
    format_type = request.args.get('format', 'csv')
    
    # Get all entries for the user
    entries = MoodTracker.query.filter_by(
        user_id=current_user.id
    ).order_by(MoodTracker.date.desc()).all()
    
    if format_type == 'csv':
        # Create CSV data
        csv_data = []
        csv_data.append(['Date', 'Mood Emoji', 'Mood Label', 'Productivity Level', 'Notes'])
        
        for entry in entries:
            csv_data.append([
                entry.date.strftime('%Y-%m-%d'),
                entry.mood_emoji,
                entry.mood_label or '',
                entry.productivity_level,
                entry.notes or ''
            ])
        
        # Convert to CSV string
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(csv_data)
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=mood_tracker_data.csv'
        response.headers['Content-type'] = 'text/csv'
        
        return response
    
    elif format_type == 'pdf':
        # This is a placeholder - in a real implementation, you would generate a PDF report
        # using a library like ReportLab or WeasyPrint
        return "PDF export not implemented yet", 501
    
    else:
        return "Unsupported export format", 400

@mood_tracker_bp.route('/api/entries')
@login_required
def get_entries():
    """API endpoint to get mood entries for the current user."""
    # Get date range from query params
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = MoodTracker.query.filter_by(user_id=current_user.id)
    
    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(MoodTracker.date >= start)
        except ValueError:
            pass
    
    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(MoodTracker.date <= end)
        except ValueError:
            pass
    
    entries = query.order_by(MoodTracker.date.desc()).all()
    
    # Convert to JSON
    result = []
    for entry in entries:
        result.append({
            'id': entry.id,
            'date': entry.date.strftime('%Y-%m-%d'),
            'mood_emoji': entry.mood_emoji,
            'mood_label': entry.mood_label,
            'productivity_level': entry.productivity_level,
            'productivity_emoji': entry.productivity_emoji,
            'notes': entry.notes
        })
    
    return jsonify(result)