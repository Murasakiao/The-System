# The System - Gamified Quest Management App

**The System** is a gamified task management web application designed to keep you productive and motivated. Turn mundane tasks into exciting quests, earn points, level up, and achieve milestones with ease. Complete daily quests and unlock achievements while staying on top of your goals.  

---

## 🚀 Features

- **User Registration and Login**: Securely create and access your account.  
- **Task Management**: Create and complete tasks (quests) effortlessly.  
- **Gamification**: Earn points, level up, and unlock achievements to stay motivated.  
- **Achievements System**: Celebrate your milestones with badges and rewards.  
- **Daily Quests**: Stay consistent with daily tasks tailored to your goals.  
- **AI Integration**: Powered by Google Generative AI for automatic quest descriptions.  

---

## 🛠 Installation

Follow these steps to set up **The System** on your local machine:

### 1. Clone the Repository
```bash
git clone https://github.com/Murasakiao/the-system.git
cd the-system
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
1. Create a `.env` file in the root directory.  
2. Add your Google Generative AI API key:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

### 5. Initialize the Database
```bash
flask db init
flask db migrate
flask db upgrade
```

### 6. Run the Application
```bash
flask run
```

The app will be available at [http://localhost:5000](http://localhost:5000).  

---

## 📖 Usage

1. Open the app in your browser at [http://localhost:5000](http://localhost:5000).  
2. Register a new account or log in if you already have one.  
3. Start creating tasks, completing quests, earning points, and leveling up!  

---

## 🤝 Contributing

We welcome contributions to make **The System** even better!  

- **Fork** the repository.  
- Create a new **branch** for your feature or bug fix.  
- Submit a **pull request** with a detailed description of your changes.  

---

## 📜 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for more details.  

---

## 📬 Contact

Feel free to reach out if you have any questions or suggestions:

- **GitHub**: [@Murasakiao](https://github.com/Murasakiao)  
- **Email**: [colesjulius3@gmail.com](mailto:colesjulius3@gmail.com)

---

Stay productive, stay motivated, and level up your life with **The System**!
```  

