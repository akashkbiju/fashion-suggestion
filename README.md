# FitFusion &bull; AI Fashion Recommendation System

FitFusion is an intelligent, AI-powered personal stylist and wardrobe recommendation platform built with **Django**, **ResNet50 Deep Convolutional Neural Networks**, and **LLMs (Google Gemini 1.5 Flash & Meta LLaMA 3 via Groq)**.

---

## 🌟 Key Features

1. **Piece Inspo & Visual Matching (Computer Vision)**:
   - Upload any apparel item (tops, trousers, dresses, footwear, or bags).
   - Extracts a **2048-dimensional feature embedding** using a pretrained **ResNet50** neural network with Global Max Pooling.
   - Computes Euclidean distance metrics with **k-Nearest Neighbors (k-NN)** to retrieve the top-6 visually matching garments from a 10,000+ item catalog.

2. **Conversational Outfit Stylist (Generative AI)**:
   - Chat-based personal stylist providing personalized head-to-toe outfit formulas.
   - Multi-tier automatic fallback system:
     - **Primary**: Google Gemini 1.5 Flash
     - **Secondary**: Meta LLaMA 3 70B via Groq
     - **Offline/Local**: Rule-based expert fashion suggestion engine

3. **Modern Luxury UI & Design**:
   - High-fashion editorial aesthetic featuring **Plus Jakarta Sans** and **Playfair Display**.
   - Interactive drag-and-drop upload studio with live image previews and progress simulations.
   - Dual-panel authentication pages (Login and Register) with client-side password strength meter, show/hide password toggle, and username or email authentication.

4. **Account & Quota Management**:
   - Monthly query tracking per user tier.
   - Owner dashboard for monitoring user activity and query metrics.

---

## 🛠️ Technology Stack

- **Backend**: Python 3, Django 5.1
- **Computer Vision & ML**: TensorFlow / Keras (ResNet50), OpenCV, NumPy, Scikit-Learn
- **Generative AI**: `google-generativeai`, `groq`
- **Database**: SQLite (configurable for PostgreSQL)
- **Frontend**: HTML5, Tailwind CSS, Alpine.js, Font Awesome 6

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/akashkbiju/fashion-suggestion.git
cd fashion-suggestion
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=your_django_secret_key
DEBUG=True
```

### 5. Run database migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Start the development server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 📂 Project Structure

```
fashionrecommend/
├── fashion/               # Main Django application
│   ├── forms.py           # Authentication & user registration forms
│   ├── models.py          # CustomUser, UserQueryCount, PlagarismChat
│   ├── views.py           # Core views (AI Stylist, ResNet50 recs, Auth)
│   ├── urls.py            # Route mappings
│   └── templates/         # UI templates (home, upload, results, auth)
├── fashionrecommend/      # Django settings and WSGI/ASGI configurations
├── static/                # Static assets (images, icons)
├── train.py               # Feature vector extraction script
├── requirements.txt       # Project dependencies
└── README.md              # Project documentation
```

---

## 📜 License
Distributed under the MIT License. See `LICENSE` for more information.
