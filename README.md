# 🛒 SmartBasket

**AI-driven shopping assistant that predicts your next likely purchase based on past behavior.**  
Combines machine learning with full-stack development for a smarter, more intuitive checkout experience.

---

## 🚀 Features

- 🧠 Neural network model predicts next likely item
- 🔒 Secure login with JWT & OAuth2
- 📦 RESTful API for user sessions and predictions
- ⚡ Redis caching for fast response times
- 💡 Responsive dashboard for live testing predictions
- 🗃️ PostgreSQL database for structured user/session data

---

## 🧰 Tech Stack

| Layer            | Tech Used                      |
|------------------|-------------------------------|
| Frontend         | React, TypeScript, React Query |
| Backend API      | FastAPI (Python)               |
| Machine Learning | TensorFlow, Scikit-learn       |
| Database         | PostgreSQL                     |
| Caching          | Redis                          |
| DevOps           | Docker, Render (deployment)    |

---

## 🧠 ML Model

- **Goal:** Predict the next item in a user’s shopping list based on prior items  
- **Architecture:** Shallow neural network (TensorFlow Sequential model)  
- **Top-3 Accuracy:** `13.7%` using minimal context  
- **Training Details:**
  - Preprocessed transactional dataset
  - Normalized and sequenced item inputs
  - Evaluated with validation + top-k metrics

---

## 🔐 API Endpoints
| Method           | Route                          | Description
|------------------|--------------------------------|------------------------|
| POST             | /token                         | Get Access token via OAuth2
| GET              | /api/v1/users/me/              | Get current user info
| POST             | /api/v1/predictions/next-item  | Predict next likely item

---

## 🛠️ Challenges Faced
🧩 Balancing sparse item sequences with limited data context

🏋️‍♂️ Training convergence on imbalanced datasets

🔄 Smooth ML model integration into backend service

---

## 🧪 Evaluation Summary
| Metric                    | Result |
| ------------------------- | ------ |
| Final Train Accuracy      | 7.8%   |
| Final Validation Accuracy | 5.5%   |
| Top-3 Accuracy            | 13.7%  |
| Validation Loss           | 4.52   |

---

## 🛣️ Roadmap
- ⏳ Implement attention-based or LSTM model
- ⏳ Add profile-based personalization
- ⏳ Improve metadata (e.g. day/time of purchase)
- ⏳ Expand UI: profile settings, trend graphs
- ⏳ CI pipeline for ML model retraining

---

## 🌐 Live Demo
- 🔗 Try SmartBasket
- First, visit the following link to spin up back-end deployment: https://smartbasket-u8bn.onrender.com
- Once back-end has launched, visit the following link to access the web app: https://smartbasket-frontend.onrender.com
- 🧪 Test Credentials:
- Login: Test
- Password: test

(Note: Deployment may take up to a minute to spin up)

---

## 📄 License & Attribution
MIT License © 2025 Evan White

> This project was built for educational and demonstration purposes, showcasing ML-driven full-stack app development.
