# Lab: Build a Command-Line Data Management UI for Restaurant Data

This repository contains a backend engineering laboratory project focused on building an interactive, menu-driven Command-Line Interface (CLI) application designed to manage structural operations and database actions for restaurant operations data.

## 🎯 Project Objective

The goal of this lab is to practice the fundamentals of building operational software workflows without complex frontend web layers. The application implements an entry-level UI using console loops that enables users to query, update, sort, and manage complex restaurant records while preserving structured relational attributes behind the scenes.

## 📁 Repository Structure

* **`restaurant_data_management.py`**: The main execution engine containing the complete operational pipeline. It implements console user input validation loops, standard sorting or filtering algorithms, and core state transformations.
* **`.gitignore`**: Standard platform file tracking exclusions to keep local python workspace properties and cache dependencies out of public branches.
* **`pyvenv.cfg`**: System configuration defining the directory mappings and settings for the project's isolated virtual environment.

## 🛠 Technologies Used

* **Language Core:** Python 3.x
* **Interface Design:** Command-Line Interface (CLI) / Terminal Console Interaction
* **Environment Strategy:** Python virtual environments (`venv`)

## 🚀 Installation and Execution

### Local Environment Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com
   cd Lab-Build-a-Command-Line-Data-Management-UI-for-Restaurant-Data
   ```

2. **Initialize and activate your virtual environment:**
   ```bash
   # On macOS/Linux
   source bin/activate
   
   # On Windows
   .\Scripts\activate
   ```

3. **Launch the CLI Application:**
   ```bash
   python restaurant_data_management.py
   ```
   Follow the numerical menu system prompted inside your terminal session to step through the data tables.

## 📈 Demonstrated Skills

* **CLI Application Architecture:** Constructing robust, crash-resilient input capture flows that sanitize raw terminal strings, filter integer inputs, and cleanly return meaningful contextual messages.
* **State Management Operations:** Structuring clean data storage logic capable of executing real-time Create, Read, Update, and Delete actions across tabular collections in volatile memory.
* **Clean Code Practices:** Decoupling operational logical routines from presentation layers to maintain a readable, highly extendable single-file Python program.
