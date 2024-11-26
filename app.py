from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
import random
import json
import os
from dotenv import load_dotenv
import google.generativeai as genai
# from transformers import GPT2LMHeadModel, GPT2Tokenizer
# from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("GEMINI_API_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data/tasks.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key
api_key = os.getenv("GEMINI_API_KEY")

# Configure the Google Generative AI library
genai.configure(api_key=api_key)

# Load the pre-trained GPT-2 model and tokenizer
# model = GPT2LMHeadModel.from_pretrained('gpt2')
# tokenizer = GPT2Tokenizer.from_pretrained('gpt2')

LEVEL_THRESHOLDS = {
    1: 0,      # Starting level
    2: 100,    # Need 100 points for level 2
    3: 250,    # Need 250 points for level 3
    4: 500,    # Need 500 points for level 4
    5: 1000,   # Need 1000 points for level 5
    6: 2000,   # Need 2000 points for level 6
    7: 3500,   # Need 3500 points for level 7
    8: 5500,   # Need 5500 points for level 8
    9: 8000,   # Need 8000 points for level 9
    10: 11000, # Need 11000 points for level 10
    11: 14500, # Need 14500 points for level 11
    12: 18500, # Need 18500 points for level 12
    13: 23000, # Need 23000 points for level 13
    14: 28000, # Need 28000 points for level 14
    15: 33500, # Need 33500 points for level 15
    16: 39500, # Need 39500 points for level 16
    17: 46000, # Need 46000 points for level 17
    18: 53000, # Need 53000 points for level 18
    19: 60500, # Need 60500 points for level 19
    20: 68500, # Need 68500 points for level 20
    21: 77000, # Need 77000 points for level 21
    22: 86000, # Need 86000 points for level 22
    23: 95500, # Need 95500 points for level 23
    24: 105500, # Need 105500 points for level 24
    25: 116000  # Need 116000 points for level 25
}

# Dictionary of quest templates
DAILY_QUEST_TEMPLATES = {
    'strength': [
        {
            'name': 'Push-ups',
            'description': 'Complete 100 push-ups. Can be broken into sets.',
            'target' : 50,
            "unit" : "reps",
            'base_reward': 5,
            'duration': 30,
            'difficulty': 'Medium'
        },
        {
            'name': 'Sit-ups',
            'description': 'Complete 100 sit-ups. Can be broken into sets.',
            'target' : 50,
            "unit" : "reps",
            'base_reward': 5,
            'duration': 30,
            'difficulty': 'Medium'
        },
        {
            'name': 'Squats',
            'description': 'Complete 100 squats. Can be broken into sets.',
            'target' : 50,
            "unit" : "reps",
            'base_reward': 5,
            'duration': 30,
            'difficulty': 'Medium'
        },
        {
            'name': 'Running',
            'description': 'Run 10 km at your own pace.',
            'target' : 5,
            "unit" : "km",
            'base_reward': 10,
            'duration': 60,
            'difficulty': 'Hard'
        }
    ],
    'intelligence': [
        {
            'name': 'Read a Book',
            'description': 'Read a book for 45 minutes.',
            'target' : 30,
            "unit" : "mins",
            'base_reward': 4,
            'duration': 45,
            'difficulty': 'Easy'
        },
        {
            'name': 'Journal',
            'description': 'Write in your journal for 30 minutes.',
            'target' : 45,
            "unit" : "mins",
            'base_reward': 3,
            'duration': 30,
            'difficulty': 'Easy'
        },
        {
            'name': 'Study a Topic',
            'description': 'Study a new topic for 1 hour.',
            'target' : 60,
            "unit" : "mins",
            'base_reward': 6,
            'duration': 60,
            'difficulty': 'Medium'
        }
    ],
    'agility': [
        {
            'name': 'Jump Rope',
            'description': 'Jump rope for 15 minutes.',
            'target' : '15',
            "unit" : "mins",
            'base_reward': 4,
            'duration': 15,
            'difficulty': 'Medium'
        },
        {
            'name': 'Stretching',
            'description': 'Complete a 30-minute stretching routine.',
            'target' : '15',
            "unit" : "mins",
            'base_reward': 3,
            'duration': 30,
            'difficulty': 'Easy'
        },
        {
            'name': 'Sprinting',
            'description': 'Complete 10 sets of 30-second sprints.',
            'target' : '15',
            "unit" : "mins",
            'base_reward': 5,
            'duration': 20,
            'difficulty': 'Hard'
        }
    ]
}


# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    points = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    quests = db.relationship('Quest', backref='user', lazy=True)
    streak = db.Column(db.Integer, default=0)
    last_completed_date = db.Column(db.DateTime, nullable=True)
    points_this_week = db.Column(db.Integer, default=0)
    achievements = db.Column(db.Text, default="")
    daily_quests = db.relationship('DailyQuestAssignment', backref='user', lazy=True)
    last_daily_quest_date = db.Column(db.Date, nullable=True)


    def update_streak(self):
        """Update the user's streak based on quest completion timing"""
        today = datetime.utcnow().date()
        
        if self.last_completed_date is None:
            # First time completing a quest
            self.streak = 1
        else:
            last_completion = self.last_completed_date.date()
            days_difference = (today - last_completion).days
            
            if days_difference == 0:
                # Same day completion, maintain current streak
                pass
            elif days_difference == 1:
                # Consecutive day, increase streak
                self.streak += 1
            else:
                # More than one day gap, reset streak
                self.streak = 1
        
        self.last_completed_date = datetime.utcnow()

    # Achievement definitions with their conditions
    ACHIEVEMENTS = {
            'WEEK_WARRIOR': {
                'id': 'WEEK_WARRIOR',
                'name': '100 Points This Week!',
                'condition': lambda user: user.points_this_week >= 100
            },
            'STREAK_MASTER': {
                'id': 'STREAK_MASTER',
                'name': '7-Day Streak Achieved!',
                'condition': lambda user: user.streak >= 7
            },
            'LEVEL_MASTER': {
                'id': 'LEVEL_MASTER',
                'name': 'Level Master!',
                'condition': lambda user: user.points >= 1000
            },
            'POINTS_PRODIGY': {
                'id': 'POINTS_PRODIGY',
                'name': '500 Points in Total!',
                'condition': lambda user: user.points >= 500
            },
            'WEEK_CHAMPION': {
                'id': 'WEEK_CHAMPION',
                'name': '200 Points This Week!',
                'condition': lambda user: user.points_this_week >= 200
            },
            'STREAK_LEGEND': {
                'id': 'STREAK_LEGEND',
                'name': '14-Day Streak!',
                'condition': lambda user: user.streak >= 14
            },
            'MONTHLY_GRINDER': {
                'id': 'MONTHLY_GRINDER',
                'name': '300 Points in Four Weeks!',
                'condition': lambda user: user.points_this_week >= 300  # Sum up points_this_week over four weeks
            },
            'STREAK_MARATHONER': {
                'id': 'STREAK_MARATHONER',
                'name': '30-Day Streak!',
                'condition': lambda user: user.streak >= 30
            },
            'HALFWAY_HERO': {
                'id': 'HALFWAY_HERO',
                'name': 'Reach Halfway to 1000 Points!',
                'condition': lambda user: user.points >= 500
            },
            'STREAK_STARTER': {
                'id': 'STREAK_STARTER',
                'name': 'First 3-Day Streak!',
                'condition': lambda user: user.streak >= 3
            },
            'WEEK_CONTRIBUTOR': {
                'id': 'WEEK_CONTRIBUTOR',
                'name': '50 Points This Week!',
                'condition': lambda user: user.points_this_week >= 50
            },
            'LIFELONG_LEARNER': {
                'id': 'LIFELONG_LEARNER',
                'name': '2000 Total Points!',
                'condition': lambda user: user.points >= 2000
            }
        }


    def add_achievement(self, achievement_id):
        """
        Add a new achievement if it doesn't already exist
        Args:
            achievement_id: The ID of the achievement to add
        """
        if achievement_id not in self.ACHIEVEMENTS:
            return False
        
        current_achievements = self.get_achievements()
        if achievement_id not in current_achievements:
            current_achievements.append(achievement_id)
            self.achievements = ";".join(current_achievements)
            return True
        return False

    def get_achievements(self):
        """Get list of achievement IDs"""
        return [ach.strip() for ach in self.achievements.split(";") if ach.strip()]

    def get_achievement_names(self):
        """Get list of achievement names for display"""
        achievement_ids = self.get_achievements()
        return [self.ACHIEVEMENTS[aid]['name'] for aid in achievement_ids if aid in self.ACHIEVEMENTS]

    def check_and_award_achievements(self):
        """Check and award any new achievements the user has earned"""
        new_achievements = []
        for achievement_id, achievement in self.ACHIEVEMENTS.items():
            if (achievement_id not in self.get_achievements() and 
                achievement['condition'](self)):
                if self.add_achievement(achievement_id):
                    new_achievements.append(achievement['name'])
        return new_achievements

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'points': self.points,
            'level': self.level,
            'streak': self.streak,
            'points_this_week': self.points_this_week,
            'achievements': self.get_achievement_names()
        }

    def calculate_level(self):
        """Calculate the user's level based on their points"""
        current_level = 1
        for level, threshold in sorted(LEVEL_THRESHOLDS.items()):
            if self.points >= threshold:
                current_level = level
            else:
                break
        return current_level

    def points_to_next_level(self):
        """Calculate how many points needed for next level"""
        current_level = self.level
        if current_level >= max(LEVEL_THRESHOLDS.keys()):
            return None  # Max level reached
        
        next_level = current_level + 1
        points_needed = LEVEL_THRESHOLDS[next_level] - self.points
        return max(0, points_needed)

    def level_progress_percentage(self):
        """Calculate percentage progress to next level"""
        if self.level >= max(LEVEL_THRESHOLDS.keys()):
            return 100
        
        current_level_threshold = LEVEL_THRESHOLDS[self.level]
        next_level_threshold = LEVEL_THRESHOLDS[self.level + 1]
        points_in_current_level = self.points - current_level_threshold
        points_needed_for_level = next_level_threshold - current_level_threshold
        
        percentage = (points_in_current_level / points_needed_for_level) * 100
        return min(100, max(0, percentage))  # Ensure between 0 and 100

    def update_points_and_level(self, points_earned):
        """Update user's points and level, return level up message if applicable"""
        old_level = self.level
        self.points += points_earned
        new_level = self.calculate_level()
        
        level_up_message = None
        if new_level > old_level:
            self.level = new_level
            level_up_message = f"Congratulations! You've reached level {new_level}!"
            # Add any level-up bonuses or rewards here
        
        return level_up_message

class DailyQuestTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)  # e.g., 'strength', 'intelligence', 'agility'
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    base_reward = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in minutes
    target = db.Column(db.Integer, nullable=True)
    unit = db.Column(db.String(20), nullable=True)
    difficulty = db.Column(db.String(20), default='Medium')

class DailyQuestAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    completed = db.Column(db.Boolean, default=False)

class Quest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    target = db.Column(db.Integer, nullable=True)
    unit = db.Column(db.String(20), nullable=True)
    tags = db.Column(db.Text, default='[]')  # Store tags as JSON string
    duration = db.Column(db.Integer, nullable=False, default=30)  # Duration in minutes
    difficulty = db.Column(db.String(20), nullable=False, default='Medium')
    reward = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completion_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    priority = db.Column(db.Integer, default=1)  # 1 (low) to 5 (high)

    def set_tags(self, tags_list):
        """Convert tags list to JSON string before storing"""
        if isinstance(tags_list, list):
            self.tags = json.dumps(tags_list)
        else:
            self.tags = '[]'

    def get_tags(self):
        """Get tags as a Python list"""
        try:
            return json.loads(self.tags)
        except (json.JSONDecodeError, TypeError):
            return []

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description or '',
            'tags': self.get_tags(),
            'duration': self.duration,
            'difficulty': self.difficulty,
            'reward': self.reward,
            'completed': self.completed,
            'completion_date': self.completion_date.strftime('%Y-%m-%d %H:%M:%S') if self.completion_date else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'due_date': self.due_date.strftime('%Y-%m-%d %H:%M:%S') if self.due_date else None,
            'priority': self.priority
        }

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
            
        user = User(
            username=username,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            flash('Logged in successfully!')
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully!')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get_or_404(session['user_id'])
    
    # Get other active quests (non-daily)
    active_quests = Quest.query.filter(
        Quest.user_id == user.id,
        Quest.completed == False,
        ~Quest.tags.like('%"daily"%')
    ).all()
    
    completed_quests = Quest.query.filter_by(
        user_id=user.id,
        completed=True
    ).all()
    
    return render_template('dashboard.html',
                         user=user,
                         completed_quests=completed_quests,
                         stats={
                             'total_points': user.points,
                             'points_this_week': user.points_this_week,
                             'streak': user.streak,
                             'achievements': user.get_achievements(),
                             'active_quests': len(active_quests),
                             'completed_quests': len(completed_quests)
                         })

@app.route('/add_quest', methods=['GET', 'POST'])
def add_quest():
    if 'user_id' not in session:
        return redirect(url_for('login'))
   
    user = User.query.get_or_404(session['user_id'])
   
    if request.method == 'POST':
        # # Debug print to see what's coming from the form
        print("Form data:", request.form)
        # tags = request.form.getlist('tags[]')
        # print("Received tags:", tags)  # Debug print

        # Get tags string and process it
        tags_string = request.form.get('tags[]', '')
        # Split by comma, strip whitespace, and filter out empty strings
        tags = [tag.strip() for tag in tags_string.split(',') if tag.strip()]
        print("Received tags:", tags)  # Debug print
        
        duration = int(request.form.get('duration', 30))
        due_date_str = request.form.get('due_date')
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Invalid due date format')
                return redirect(url_for('add_quest'))
        
        new_quest = Quest(
            name=request.form['name'],
            description=request.form['description'],
            duration=duration,
            difficulty=request.form.get('difficulty', 'Medium'),
            reward=int(request.form['reward']),
            priority=int(request.form.get('priority', 1)),
            due_date=due_date,
            user_id=session['user_id']
        )
        
        new_quest.set_tags(tags)
        print("Tags after setting:", new_quest.tags)  # Debug print
        
        db.session.add(new_quest)
        db.session.commit()
        
        # Verify tags after commit
        db.session.refresh(new_quest)
        print("Tags after commit:", new_quest.tags)  # Debug print
        
        flash('Quest added successfully!')
        return redirect(url_for('dashboard'))
   
    return render_template('add_quest.html', user=user)

@app.route('/quests')
def quests():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get_or_404(session['user_id'])
    
    # Generate daily quests if needed
    generate_daily_quests(user.id)
    
    # Get today's daily quests
    today = date.today()
    daily_quests = Quest.query.filter(
        Quest.user_id == user.id,
        Quest.created_at >= today,
        Quest.tags.like('%"daily"%'),
        # Quest.completed == False
    ).all()
    
    # Get regular active quests (non-daily)
    active_quests = Quest.query.filter(
        Quest.user_id == user.id,
        Quest.completed == False,
        ~Quest.tags.like('%"daily"%')
    ).all()
    
    # Get daily training category
    daily_assignment = DailyQuestAssignment.query.filter_by(
        user_id=user.id,
        assigned_date=today
    ).first()
    
    daily_category = daily_assignment.category if daily_assignment else None
    
    return render_template('quests.html', 
                         user=user,
                         daily_quests=daily_quests,
                         active_quests=active_quests,
                         daily_category=daily_category
                         )

@app.route('/edit_quest/<int:quest_id>', methods=['GET', 'POST'])
def edit_quest(quest_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    quest = Quest.query.get_or_404(quest_id)
    if quest.user_id != session['user_id']:
        flash('Unauthorized action')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        quest.name = request.form['name']
        quest.description = request.form['description']
        quest.set_tags(request.form.getlist('tags[]'))
        quest.duration = int(request.form['duration'])
        quest.difficulty = request.form['difficulty']
        quest.reward = int(request.form['reward'])
        quest.priority = int(request.form.get('priority', 1))
        
        due_date_str = request.form.get('due_date')
        if due_date_str:
            try:
                quest.due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Invalid due date format')
                return redirect(url_for('edit_quest', quest_id=quest_id))
        else:
            quest.due_date = None
        
        db.session.commit()
        flash('Quest updated successfully!')
        return redirect(url_for('dashboard'))
    
    return render_template('edit_quest.html', quest=quest)

@app.route('/delete_quest/<int:quest_id>', methods=['POST'])
def delete_quest(quest_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    quest = Quest.query.get_or_404(quest_id)
    if quest.user_id != session['user_id']:
        flash('Unauthorized action')
        return redirect(url_for('dashboard'))
    
    db.session.delete(quest)
    db.session.commit()
    flash('Quest deleted successfully!')
    return redirect(url_for('dashboard'))

@app.route('/suggest_description', methods=['POST'])
def suggest_description():
    try:
        quest_title = request.json['questTitle']
        suggested_description = generate_description(quest_title)
        return jsonify({'suggestedDescription': suggested_description})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/complete_quest/<int:quest_id>', methods=['POST'])
def complete_quest(quest_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    quest = Quest.query.get_or_404(quest_id)
    user_id = session['user_id']
    
    if quest.user_id != user_id:
        flash('Unauthorized action')
        return redirect(url_for('dashboard'))
    
    if not quest.completed:
        quest.completed = True
        quest.completion_date = datetime.utcnow()
        user = User.query.get(user_id)
        
        total_reward = quest.reward
        # Update points, level, and get level up message if any
        level_up_message = user.update_points_and_level(total_reward)
        
        # Update streak and points_this_week
        user.points += total_reward
        if user.points_this_week is None:
            user.points_this_week = 0
        user.points_this_week += total_reward
        
        # Use the new streak update method
        user.update_streak()
        
        # Check and award achievements
        new_achievements = user.check_and_award_achievements()
        
        # Get today's daily quests
        today = date.today()
        daily_quests = Quest.query.filter(
            Quest.user_id == user_id,
            Quest.created_at >= today,
            Quest.tags.like('%"daily"%')
        ).all()
        
        # Check if all daily quests are completed
        all_daily_completed = all(dq.completed for dq in daily_quests)
        
        # If there are daily quests and they're all completed, update the assignment
        if daily_quests and all_daily_completed:
            assignment = DailyQuestAssignment.query.filter_by(
                user_id=user_id,
                # date=today
            ).first()
            
            if assignment:
                assignment.completed = True
                flash('Congratulations! You have completed all daily quests. Click here to view rewards', 'success')
        
        db.session.commit()
        
        # Flash messages for quest completion and achievements
        flash(f'Quest completed! You earned {total_reward} points!')
        if level_up_message:
            flash(level_up_message, 'success')
        for achievement in new_achievements:
            flash(f'New Achievement Unlocked: {achievement}', 'success')
    
    return redirect(url_for('dashboard'))

def initialize_quest_templates():
    """Initialize the database with quest templates if they don't exist"""
    with app.app_context():
        if DailyQuestTemplate.query.count() == 0:
            for category, quests in DAILY_QUEST_TEMPLATES.items():
                for quest in quests:
                    template = DailyQuestTemplate(
                        category=category,
                        name=quest['name'],
                        description=quest['description'],
                        target=quest.get('target'),
                        unit=quest.get('unit'),
                        base_reward=quest['base_reward'],
                        duration=quest['duration'],
                        difficulty=quest['difficulty']
                    )
                    db.session.add(template)
            db.session.commit()

def get_daily_training_category(user_id):
    """Determine the training category for the day"""
    # Get the user's last assignment
    last_assignment = DailyQuestAssignment.query.filter_by(
        user_id=user_id
    ).order_by(DailyQuestAssignment.assigned_date.desc()).first()
    
    # List of all categories
    categories = list(DAILY_QUEST_TEMPLATES.keys())
    
    if not last_assignment:
        # If no previous assignment, randomly choose a category
        return random.choice(categories)
    
    # Remove the last category from the list to avoid repetition
    categories.remove(last_assignment.category)
    return random.choice(categories)

def generate_daily_quests(user_id):
    """Generate daily quests for a user"""
    today = date.today()
    user = User.query.get(user_id)
    
    # Check if user already has quests for today
    if user.last_daily_quest_date == today:
        return
    
    # Get training category for today
    category = get_daily_training_category(user_id)
    
    # Create daily quest assignment
    assignment = DailyQuestAssignment(
        user_id=user_id,
        assigned_date=today,
        category=category,
        completed=False
    )
    db.session.add(assignment)
    
    # Get quest templates for the category
    templates = DailyQuestTemplate.query.filter_by(category=category).all()
    
    # Create quests from templates
    for template in templates:
        quest = Quest(
            name= template.name,
            description=template.description,
            target=template.target,
            unit=template.unit,
            duration=template.duration,
            difficulty=template.difficulty,
            reward=template.base_reward,
            user_id=user_id,
            tags=json.dumps([category, 'daily']),
            due_date=datetime.combine(today, datetime.max.time()),  # End of today
            priority=3  # Medium-high priority for daily quests
        )
        db.session.add(quest)
    
    user.last_daily_quest_date = today
    db.session.commit()

def check_daily_quest_completion(user_id):
    """Check if all daily quests for today are completed"""
    today = date.today()
    daily_quests = Quest.query.filter(
        Quest.user_id == user_id,
        Quest.created_at >= today,
        Quest.tags.like('%"daily"%')
    ).all()
    
    if not daily_quests:
        return False
    
    all_completed = all(quest.completed for quest in daily_quests)
    if all_completed:
        # Mark the daily assignment as completed
        assignment = DailyQuestAssignment.query.filter_by(
            user_id=user_id,
            assigned_date=today
        ).first()
        if assignment:
            assignment.completed = True
            db.session.commit()
    
    return all_completed

def generate_description(quest_title: str):
    """Generate a short, stylized quest description based on the quest title, with a gamified and Solo Leveling-inspired theme.
    
    Args:
        quest_title (str): The title of the quest to generate a description for
    """
    try:
        # Create the model
        generation_config = {
            "temperature": 1,
            "top_p": 0.75,
            "top_k": 44,
            "max_output_tokens": 254,
            "response_mime_type": "text/plain",
        }
        
        model = genai.GenerativeModel(
            model_name="gemini-exp-1114",
            generation_config=generation_config,
        )
        
        chat_session = model.start_chat(history=[])
        prompt = (
            f"Generate a single direct quest description for the quest titled: '{quest_title}'. "
            "Make it brief (2-3 sentences), direct and real-world-based experience,  "
            "Focus on the challenge and potential rewards. The last 2 sentences should be direct steps that will guide the player on the task"
        )
        
        response = chat_session.send_message(prompt)
        
        # Extract the text content from the response
        if response.text:
            return response.text.strip()
        return "Failed to generate description."
        
    except Exception as e:
        print(f"Error generating description: {str(e)}")
        return "Failed to generate description."

# def generate_description(quest_title):
#     # Create the model
#     generation_config = {
#         "temperature": 1,
#         "top_p": 0.95,
#         "top_k": 64,
#         "max_output_tokens": 254,
#         "response_mime_type": "text/plain",
#     }

#     model = genai.GenerativeModel(
#         model_name="gemini-exp-1114",
#         generation_config=generation_config,
#     )

#     chat_session = model.start_chat(history=[])

#     response = chat_session.send_message(f"Can you suggest a single quest description from this quest title: {quest_title}")

    # """Generate a short, stylized quest description based on the quest title, with a gamified and Solo Leveling-inspired theme."""
    
    # # Customized prompt to influence the GPT-2 generation style
    # prompt = (f"Quest Title: {quest_title}\n\n"
    #           "Description:")
    
    # input_ids = tokenizer.encode(prompt, return_tensors='pt')
    
    # # Generate the description with adjusted parameters for more accurate output
    # output_ids = model.generate(
    #     input_ids, 
    #     num_return_sequences=1, 
    #     max_length=60,           # Shorter max length for concise descriptions
    #     do_sample=True, 
    #     top_k=30,                 # Lower top_k to encourage relevant words
    #     top_p=0.9                 # Slightly lower top_p to favor coherence over randomness
    # )[0]
    
    # # Decode and return the generated description
    # suggested_description = tokenizer.decode(output_ids, skip_special_tokens=True)
    
    # if "Description:" in suggested_description:
    #     suggested_description = suggested_description.split("Description:")[1].strip()
    
    # return suggested_description
    # return response
    # return 


def init_db():
    with app.app_context():
        db.create_all()
        initialize_quest_templates()
        
        if not User.query.first():
            default_user = User(
                username="demo",
                password_hash=generate_password_hash("demo123")
            )
            db.session.add(default_user)
            db.session.commit()

def init_app(app):
    with app.app_context():
        db.create_all()
        init_db()

if __name__ == '__main__':
    init_app(app)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    app.run(debug=True)
else:
    init_app(app)
