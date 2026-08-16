IMDb 2026 Movie Scraper 🎬

A Python-based IMDb movie scraper that collects movie information and exports the results into Excel files for easy analysis and management.

<img width="1400" height="735" alt="image" src="https://github.com/user-attachments/assets/5e729430-e8f4-43a1-9565-7365a357c3b9" />


📌 Project Overview

IMDb 2026 Scraper is an automation project built with Python and Selenium to collect movie information from IMDb pages.

The scraper is designed to extract useful movie details such as:

🎬 Movie title

📅 Release year

⭐ IMDb rating

🎭 Genres

🎥 Directors

👥 Cast

⏱️ Runtime

📝 Plot

🆔 IMDb ID

🖼️ Poster URL

📆 Release date

The collected information can then be exported to Excel for further analysis.

✨ Features

Automated IMDb data collection

Selenium-based browser automation

Movie list and movie-detail parsing

Extraction of movie metadata

Poster URL collection

Excel export

Logging for scraper execution

Configurable scraper settings

Organized project structure

🛠️ Tech Stack

Technology

Purpose

Python 3.10

Core programming language

Selenium

Browser automation and web scraping

BeautifulSoup

HTML parsing and data extraction

Pandas

Data processing

OpenPyXL

Excel file generation

IMDb

Movie data source

📂 Project Structure

IMDB_2026_Scraper/
│
├── images/
│   └── project-preview.png
│
├── logs/
│   └── scraper logs
│
├── output/
│   └── generated Excel files
│
├── utils/
│   ├── excel.py
│   ├── logger.py
│   └── scraper.py
│
├── config.py
├── debug_scrape.py
├── requirements.txt
├── scraper.py
├── test_scraper.py
├── test_selectors.py
├── .gitignore
└── README.md

🚀 Getting Started

1. Clone the repository

git clone https://github.com/Thirubts2005/Selenium_Project.git
cd Selenium_Project

2. Create a virtual environment

python -m venv venv

Activate it on Windows:

venv\Scripts\activate

3. Install dependencies

pip install -r requirements.txt

4. Run the scraper

python scraper.py

The scraped movie data will be saved in the output/ directory.

📊 Sample Output

The scraper exports movie information into Excel format.

Example fields:

Title
Year
Rating
Genres
Directors
Cast
Runtime
Plot
IMDb ID
Poster URL
Release Date

🖥️ Development Environment

The project was developed using:

Visual Studio Code

Python 3.10 (64-bit)

Selenium

Git & GitHub

⚠️ Disclaimer

This project is created for educational and learning purposes. Please respect IMDb's terms of service, robots.txt, rate limits, and applicable laws when using automated scraping tools.

👨‍💻 Author

Thiru B

B.Tech – Artificial Intelligence & Data Science

GitHub: @Thirubts2005

⭐ If you found this project useful, consider giving the repository a star!
