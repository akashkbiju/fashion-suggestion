# FitFusion &bull; Next-Gen AI Fashion Stylist & Recommendation Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.1-092E20.svg?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-FF6F00.svg?logo=tensorflow&logoColor=white)](https://www.tensorflow.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.x-38B2D6.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

**FitFusion** is an intelligent, high-fashion AI stylist and wardrobe recommendation platform. It combines **Deep Convolutional Neural Networks (ResNet50)** for computer vision similarity search with **Generative LLMs (Google Gemini 1.5 Flash & Meta LLaMA 3 via Groq)** to provide personalized outfit formulas, visual apparel matching, and curated aesthetics.

---

## 🌟 Key Features

### 1. 🔍 Piece Inspo & Visual Apparel Matching (Computer Vision)
- **Neural Feature Extraction**: Upload any photo of a shirt, dress, jacket, pants, sneakers, or handbag. Pretrained **ResNet50** (with classification top removed and paired with `GlobalMaxPooling2D`) extracts a **2048-dimensional normalized feature vector**.
- **Nearest Neighbor Search**: Scikit-Learn's `NearestNeighbors` algorithm calculates Euclidean distances against a precomputed catalog of **10,000+ fashion garments**, returning the **top 6 closest matching styles**.
- **Interactive Studio UI**: Drag-and-drop dropzone, live instant image preview, file validation (PNG, JPG, WEBP &le; 10MB), and dynamic scanning progress bar.

### 2. 💬 Conversational Outfit Stylist (Generative AI)
- **Personalized Outfit Formulas**: Interactive AI chat assistant that creates complete top-to-bottom outfit formulas based on occasion, weather, silhouette, and personal preferences.
- **Fail-Safe Multi-Tier Fallback Architecture**:
  1. **Primary**: Google Gemini 1.5 Flash (`models/gemini-1.5-flash`)
  2. **Secondary / Low-Latency**: Meta LLaMA 3 70B (`llama3-70b-8192` via Groq)
  3. **Local Rule-Based Expert Engine**: Offline fallback engine handling formal, party, winter, summer, athletic, and smart-casual queries with zero downtime.

### 3. 🎨 Curated Aesthetics & Moodboards
- Interactive aesthetic showcases on the Home Page:
  - **🍸 Quiet Luxury**: Double-faced wool blazers, cashmere knitwear, and Belgian loafers.
  - **🖤 Streetwear Luxe**: Boxy heavyweight hoodies, wide-leg utility cargo denim, and architectural trainers.
  - **☕ Dark Academia**: Merino turtlenecks, tailored tweed herringbone overcoats, and Chelsea boots.
  - **🌿 Minimalist Chic**: Crisp oversized poplin button-downs, straight-leg denim, and court sneakers.

### 4. ⭐ Community Feedback & Review System
- Public feedback submission form with an interactive **5-star rating component** and topic categorizer (Outfit Recs, Piece Inspo, UI/UX, Feature Requests).
- Verified community reviews grid on the home page.
- Asynchronous AJAX submission with smooth inline confirmation banners.

### 5. 👑 Dual Admin & Management Suites
- **Django Admin Panel (`/admin/`)**: Comprehensive database access for staff users to inspect, filter, search, and manage models (`Feedback`, `CustomUser`, `UserQueryCount`, `PlagarismChat`).
- **Owner Executive Dashboard (`/owner-dashboard/`)**: Dedicated in-app admin suite for the platform owner to:
  - Monitor member query utilization (Live, Chat, File similarity queries).
  - Review, toggle featured visibility (`is_featured`), or delete community feedback entries.
  - View real-time average rating scores and review analytics.

---

## 🏗️ System Architecture

```
User Upload / Chat Prompt
           │
           ├── [Image Upload] ────────► ResNet50 Feature Extractor (2048-D)
           │                                    │
           │                                    ▼
           │                           k-Nearest Neighbors (k-NN)
           │                                    │
           │                                    ▼
           │                          Top 6 Matching Garments
           │
           └── [Text / Styling Chat] ──► Multi-Tier LLM Router
                                                │
                                    ┌───────────┼───────────┐
                                    ▼           ▼           ▼
                                 Gemini       Groq     Rule-Based
                               1.5 Flash    LLaMA 3     Fallback
```

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Web Framework** | Python 3, Django 5.1 (ORM, Sessions, Auth, Admin) |
| **Computer Vision** | TensorFlow / Keras (ResNet50), OpenCV, NumPy, Scikit-Learn |
| **Generative AI** | `google-generativeai`, `groq` SDK |
| **Frontend** | HTML5, Tailwind CSS, Alpine.js, Font Awesome 6 |
| **Database** | SQLite3 (Production-ready for PostgreSQL / MySQL) |

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/akashkbiju/fashion-suggestion.git
cd fashion-suggestion
```

### 2. Create and activate a virtual environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the project root directory:
```env
GEMINI_API_KEY=your_google_gemini_api_key
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=your_django_secret_key
DEBUG=True
```

### 5. Run database migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create an administrator account
```bash
python manage.py createsuperuser
```

### 7. Run the development server
```bash
python manage.py runserver
```
Navigate to [`http://127.0.0.1:8000/`](http://127.0.0.1:8000/) in your browser.

---

## 🗺️ Key Routes & Endpoints

| URL Pattern | View Function | Description |
|---|---|---|
| `/` | `home` | Modern landing page with interactive aesthetics and reviews |
| `/login/` | `login_view` | Dual username/email authentication with password toggle |
| `/register/` | `register` | User onboarding with live password strength meter |
| `/dashboard/` | `dashboard` | User styling studio portal |
| `/fashion/` | `fashion_recommend` | Piece Inspo & drag-and-drop image upload studio |
| `/file-review/` | `review_file` | Conversational AI outfit stylist chat |
| `/feedback/` | `submit_feedback` | Public feedback submission endpoint (AJAX / Form) |
| `/owner-dashboard/` | `owner_dashboard` | Executive dashboard with feedback moderation & user quotas |
| `/admin/` | Django Admin | Administrative database management interface |

---

## 📂 Project Structure

```
fashionrecommend/
├── fashion/                        # Main Django application
│   ├── migrations/                 # Database schema migrations
│   ├── templates/                  # Frontend UI templates
│   │   ├── premade/home.html       # Landing page & style showcase
│   │   ├── fashion/upload.html     # Piece Inspo drag-and-drop studio
│   │   ├── fashion/results.html    # Visual recommendation results grid
│   │   ├── login.html              # Modern dual-panel sign-in
│   │   ├── register.html           # Registration with security meter
│   │   ├── dashboard.html          # Member styling studio hub
│   │   └── owner_dashboard.html    # Executive feedback moderation suite
│   ├── admin.py                    # Django admin registrations
│   ├── forms.py                    # Authentication & feedback forms
│   ├── models.py                   # CustomUser, Feedback, UserQueryCount
│   ├── urls.py                     # App routing
│   └── views.py                    # Computer vision & generative AI views
├── fashionrecommend/               # Project configuration (settings, wsgi, asgi)
├── models/                         # Precomputed feature vectors & models
├── static/                         # Static assets (images, fonts, stylesheets)
├── train.py                        # Feature vector precomputation script
├── requirements.txt                # Python dependencies
├── .env                            # Environment secrets (ignored by Git)
├── .gitignore                      # Git exclusion rules
└── README.md                       # Project documentation
```

---

## 📜 License
This project is licensed under the MIT License - see the `LICENSE` file for details.

## DEPLOYED IN RENDER
