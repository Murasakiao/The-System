The System - Gamified Quest Management App

The System is a web application that helps users manage their tasks with a gamified twist. Earn points, level up, unlock achievements, and complete daily quests to stay productive and motivated.
Features

    User registration and login

    Create, edit, and complete tasks (quests)

    Earn points and level up

    Achievements system for milestones

    Daily quests for consistent productivity

    Integration with Google Generative AI for quest descriptions

Installation

    Clone the repository:
    Copy

    git clone https://github.com/yourusername/taskmaster.git

    Create a virtual environment:
    Copy

    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

    Install dependencies:
    Copy

    pip install -r requirements.txt

    Set up environment variables:

        Create a .env file in the root directory.

        Add your Google Generative AI API key:
        Copy

        GEMINI_API_KEY=your_api_key_here

    Initialize the database:
    Copy

    flask db init
    flask db migrate
    flask db upgrade

    Run the app:
    Copy

    flask run

Usage

    Access the app at http://localhost:5000 in your web browser.

    Register a new account or log in if you already have one.

    Create tasks, complete them to earn points, and level up!

Contributing

Contributions are welcome! Please read the installation instructions and feel free to open issues or pull requests.
License

MIT License
Contact

    GitHub: @Murasakiao

    Email: colesjulius3@gmail.com
