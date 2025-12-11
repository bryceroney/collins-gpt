from datetime import datetime
from flask import Blueprint, render_template

bp = Blueprint('main', __name__)


def get_greeting():
    """Return time-appropriate greeting."""
    hour = datetime.now().hour
    if hour < 12:
        return "Good Morning"
    elif hour < 17:
        return "Good Afternoon"
    else:
        return "Good Evening"


@bp.route('/')
def index():
    """Dashboard home page."""
    modules = [
        {
            "id": "dixer-writer",
            "title": "Question Time Dixer Writer",
            "description": "Generates friendly constituency questions for backbenchers to ask during Question Time.",
            "icon": "bi-mic-fill",
            "color": "primary"
        },
        {
            "id": "hot-issues",
            "title": "Hot Issues Brief Updater",
            "description": "Scans the latest news to update the daily briefing notes on emerging issues.",
            "icon": "bi-newspaper",
            "color": "info"
        }
    ]

    return render_template(
        'dashboard.html',
        greeting=get_greeting(),
        modules=modules
    )


