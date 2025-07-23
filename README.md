<div align="center">

<!-- You can create a simple banner image/logo and upload it to your repo -->
<!-- For now, it's a placeholder. Replace 'path/to/your/banner.png' -->
<!-- Or delete this line if you don't have a banner -->
<img src="path/to/your/banner.png" alt="Shiva Voice Assistant Banner" width="700"/>

# Shiva Voice Assistant (Advanced)

**A desktop voice assistant built with Python, featuring real-time audio noise reduction, direct local system control, and a hybrid command engine powered by Google's Generative AI.**

<p>
    <img alt="Python Version" src="https://img.shields.io/badge/python-3.8+-blue.svg">
    <img alt="License" src="https://img.shields.io/badge/License-MIT-yellow.svg">
    <img alt="Status" src="https://img.shields.io/badge/status-active-success.svg">
</p>

</div>

---

## 🌟 Key Features

-   **🎤 Advanced Noise Reduction:** Utilizes `noisereduce` to clean microphone audio in real-time, significantly improving command recognition accuracy in noisy environments.
-   **🧠 Hybrid Command Engine:** Instantly handles predefined local commands (e.g., "open Notepad") for speed and falls back seamlessly to a powerful generative AI for complex or unknown queries.
-   **🤖 Generative AI Integration:** Powered by **Google's Gemini** for robust natural language understanding, Q&A, weather reports, fun facts, and more.
-   **💻 Direct System Control:** Open local applications, files (PDF, DOCX), and play local media (music, videos). Can even extract file paths directly from voice commands.
-   **🌐 Web & Information Access:** Open websites, search Google, and fetch summaries from Wikipedia.
-   **💡 Engaging User Interface:** A full-screen, stable animated background provides constant visual feedback that the assistant is active.
-   **🛠️ Utility Functions:** Includes a flexible voice-activated timer that understands seconds, minutes, and hours.

---

## 🚀 Technology Stack

| Component             | Technology / Library                                                                    |
| --------------------- | --------------------------------------------------------------------------------------- |
| **Language**          | Python 3.x                                                                              |
| **Voice & Audio**     | `speech_recognition`, `PyAudio`, `pyttsx3`, `numpy`, `noisereduce`                        |
| **Artificial Intelligence** | `google-generativeai` (for Google Gemini)                                               |
| **GUI**               | `tkinter`, `Pillow`                                                                     |
| **System & Web**      | `os`, `webbrowser`, `wikipedia`, `re`                                                   |
| **Concurrency**       | `threading`, `asyncio`                                                                  |
| **Configuration**     | `python-dotenv`                                                                         |

---

## 🛠️ Setup and Installation

### Prerequisites

-   Python 3.8 or newer
-   Git command-line tool
-   A working microphone and speakers

### Installation Steps

1.  **Clone the Repository**
    Open your terminal or command prompt and clone this repository:
    ```bash
    git clone https://github.com/shyamyadavji/Shiva-Voice-Assistant.git
    cd Shiva-Voice-Assistant
    ```

2.  **(Recommended) Create a Virtual Environment**
    It's best practice to create a virtual environment to manage project dependencies cleanly.
    ```bash
    # For Windows
    python -m venv venv
    venv\Scripts\activate

    # For macOS / Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    Install all the required Python libraries using the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Your Environment File**
    This is a crucial step to securely store your API key.
    -   Create a new file named `.env` in the root directory of the project.
    -   Open the `.env` file and add your Google AI API key:
        ```
        GOOGLE_API_KEY="YOUR_SECRET_API_KEY_HERE"
        ```
    -   *This file is intentionally ignored by Git and will not be uploaded, keeping your key safe.*

---

## ⚙️ Usage & Configuration

### Running the Assistant
To start Shiva, run the main script from your terminal:
```bash
python shiv.py