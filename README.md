---


# 🧠 OCR Platform with LLaMA 3.2-Vision + Docker

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A fully containerized OCR (Optical Character Recognition) platform powered by the `llama3.2-vision` model via [Ollama](https://ollama.com). This application is exposed through a simple Flask API and allows for the uploading of doctor receipts (in PDF), extraction of structured data, and the generation of a PDF summary for download. 

<img width="1536" height="1024" alt="OCR Platform Workflow Diagram" src="https://github.com/user-attachments/assets/0be0a3f2-8e4f-4128-96a7-f35360f9879d" />
---

## 🚀 Features

-   **Advanced OCR**: Utilizes the powerful `llama3.2-vision` model through Ollama for accurate text extraction.
-   **Multi-format Support**: Accepts PDF files for OCR processing via a user-friendly web interface or a direct API endpoint.
-   **Structured Data Extraction**: Specifically designed to extract key information from medical receipts, including:
    -   Insurance company name
    -   Patient’s full name
    -   10-digit insurance number
-   **Automated PDF Generation**: Exports the extracted results into a ready-to-send PDF letter.
-   **Secure Access**: The web interface and API are secured using Basic Authentication.
-   **Dockerized Environment**: The entire application and its dependencies run in isolated Docker containers, ensuring consistency and ease of deployment with a single command.

---

## 📸 Example Output

The API returns a structured JSON object with the extracted information.
**JSON Output:**
```json
{
  "ocr_insurance_company": "AOK Baden-Württemberg",
  "name": "Müller Anna",
  "insurance_number": "K123456789"
}
```

---

## 🛠️ Technology Stack

-   **Backend**: Flask (Python)
-   **ML Model Server**: Ollama
-   **OCR Model**: `llama3.2-vision`
-   **Containerization**: Docker & Docker Compose

---

## 🐳 How to Run

### Prerequisites

Before you begin, ensure you have the following installed and running on your local machine:
*   [Docker](https://docs.docker.com/get-docker/)
*   [Docker Compose](https://docs.docker.com/compose/install/)

### Installation and Launch

1.  **Clone the Repository**

    Open your terminal and clone the project repository:
    ```bash
    git clone git@github.com:Mimou-AJ/llama3.2-vision-flask.git
    cd llama3.2-vision-flask
    ```

2.  **Run with Docker Compose**

    Execute the following command in the root directory of the project:
    ```bash
    docker-compose up -d
    ```

    This command will automatically:
    -   Build the Docker image for the Python Flask application.
    -   Start the Ollama model server in a separate container.
    -   Download the `llama3.2-vision` model (if it's not already present in the Docker volume).
    -   Launch the web interface, which will be accessible at `http://localhost:5000`.

---

## 🌐 API Endpoints

All endpoints are secured and require Basic Authentication.

### **Web Interface**

-   **Endpoint**: `/home`
-   **Method**: `GET`, `POST`
-   **Description**: Provides a secure web interface for uploading PDF or image files for processing.

### **API for OCR**

-   **Endpoint**: `/api/v1/OCR/image2text/upload`
-   **Method**: `POST`
-   **Description**: Uploads and processes a file. It returns the initial prediction from the OCR model.

-   **Endpoint**: `/api/v1/OCR/image2text/confirm`
-   **Method**: `POST`
-   **Description**: Takes the potentially corrected data, finalizes it, and generates the PDF letter and a corresponding ZIP archive.

---

## 📦 Model Storage with Docker Volume

To ensure persistence and avoid re-downloading the large `llama3.2-vision` model every time the application is restarted, the model is stored in a named Docker volume called `model-data`.

You can manage and inspect this volume using standard Docker commands:

-   **List all Docker volumes:**
    ```bash
    docker volume ls
    ```

-   **Inspect the `model-data` volume:**
    ```bash
    docker volume inspect model-data
    ```

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
