# 🛡️ Malware Detection Web Application

A web-based malware detection system using a hybrid machine learning model. This project is built with a **FastAPI** backend and **React.js** frontend, using a **SqlLite** database for data storage and an **Anaconda** environment for Python dependencies.


---

## ⚙️ Technologies Used

- **Backend**: FastAPI, SQLAlchemy, scikit-learn, joblib
- **Frontend**: React.js
- **Database**: SqlLite
- **Environment**: Anaconda
- **ML Models**: K-means, SVM (hybrid ensemble)

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git https://github.com/TIRP-Group3/design3
cd design3
conda env create -f anacondapk.yaml
conda activate malware-detection
cd backend
uvicorn main:app --reload
cd frontend
npm install
npm run dev
```


Figmaa Prototype Link:
  https://www.figma.com/design/Aj1VbFoNF7JrPPhFnNsbwt/Dashboard?node-id=0-1&t=UL7LNfk2Pm8JpDar-1
