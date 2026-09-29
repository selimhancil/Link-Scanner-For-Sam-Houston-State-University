<div align="center">

![EduLink Inspector Banner](assets/banner.png)

# EduLink Inspector
### University Broken Link & Web Health Auditor

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg?style=flat-square)](https://github.com/selimhancil/Link-Scanner-For-Sam-Houston-State-University)

<p align="center">
  A fast, accurate, and noise-free link auditor built for academic institutions and enterprise web portals.<br>
  Eliminates false-positives from bot-protected services like social media, and flags genuine 404s and server issues.
</p>

[Quickstart](#-quickstart) • [Key Features](#-key-features) • [Screenshot](#-preview) • [Architecture](#-project-structure) • [Configuration](#-configuration)

</div>

---

## 📸 Preview

<div align="center">
  <img src="assets/screenshot.png" alt="EduLink Inspector Dashboard" width="900" style="border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);" />
</div>

---

## 🌟 Key Features

- **🛡️ Smart Anti-Bot False-Positive Filtering:**
  University web pages frequently link to social profiles (`Facebook`, `Instagram`, `LinkedIn`, `X / Twitter`, `YouTube`). These platforms block automated scrapers with `HTTP 403 Forbidden` or `HTTP 429 Too Many Requests`. EduLink Inspector automatically distinguishes bot protections from real broken links, preventing false alarms.

- **🌐 Domain Boundary & Subdomain Support:**
  Crawling strictly adheres to the university's base domain while providing seamless support for department and faculty subdomains (e.g., `cs.univ.edu`, `grad.univ.edu`).

- **⚡ Dual-Phase Link Verification (HEAD + GET):**
  Uses lightweight HTTP `HEAD` requests for peak performance, falling back to streaming `GET` verification when web servers improperly reject `HEAD` methods.

- **📊 Consolidated Issue Reporting & De-duplication:**
  Broken links appearing across multiple pages (e.g., in persistent navigation menus or footers) are consolidated into a single record with occurrence counts and discovery references.

- **📈 Executive Health KPI Dashboard:**
  Real-time KPI metrics displaying **Pages Crawled**, **Links Checked**, **Unique Broken Links**, and an overall **Link Health Score %**.

- **📑 Categorized Tabbed Views & CSV Export:**
  Sort and filter issues by category (`All Broken Links`, `404 Not Found`, `Server & Network Errors`), and export the entire audit report to an Excel-compatible UTF-8 CSV with one click.

---

## 📁 Project Structure

```
Link-Scanner/
├── assets/
│   ├── banner.png          # Repository branding banner
│   └── screenshot.png      # Application interface preview
├── app.py                  # Streamlit web dashboard & executive KPI interface
├── crawler.py              # Core crawling engine, link validator & BFS orchestrator
├── requirements.txt        # Python dependency manifest
├── .gitignore              # Environment and cache ignore rules
└── README.md               # Project documentation
```

---

## 🚀 Quickstart

### 1. Clone the Repository

```bash
git clone https://github.com/selimhancil/Link-Scanner-For-Sam-Houston-State-University.git
cd Link-Scanner-For-Sam-Houston-State-University
```

### 2. Set Up Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Launch the Web Application

```bash
streamlit run app.py
```

The application will automatically open in your default browser at `http://localhost:8501`.

---

## ⚙️ Configuration

| Parameter | Default | Description |
| :--- | :---: | :--- |
| **Exclude Social Media** | `True` | Ignores known social networks that block automated HTTP bots |
| **Audit Scope** | `All Links` | Choose between auditing all links or university-internal links only |
| **Include Subdomains** | `True` | Treats subdomains (`faculty.univ.edu`) as internal domain pages |
| **Max Pages to Crawl** | `30` | Safety limit to prevent overwhelming the target server |
| **Request Timeout** | `5s` | Maximum wait duration per connection query |

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
