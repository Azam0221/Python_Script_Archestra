# Sentinel Bridge (Agent Proxy)

**Sentinel Bridge** is a lightweight, asynchronous Python middleware built with **Starlette** and **Uvicorn**. It acts as a secure gateway between an AI Agent and a **Spring Boot** backend, enforcing permission controls, logging, and a "kill switch" mechanism.

It implements a **JSON-RPC 2.0** style protocol (compatible with Model Context Protocol standards) to handle tool discovery and execution requests.

## Features

* **JSON-RPC Interface:** Handles `initialize`, `tools/list`, and `tools/call` methods.
* **Security Gating:**
    * **Kill Switch:** Checks the Java backend before every action to see if the agent has been terminated.
    * **Human-in-the-Loop:** Implements a polling mechanism for `request_permission` tools, waiting for Admin approval via the Java backend.
* **Async Logging:** Streams agent activity logs directly to the Spring Boot API.
* **Tool Proxy:** Forwards approved tool calls (like `deploy`, `status`) to the backend for execution.

## Tech Stack

* **Python 3.10+**
* **Starlette** (ASGI Framework)
* **Uvicorn** (ASGI Server)
* **HTTPX** (Async HTTP Client)

## Prerequisites

* Python 3.8 or higher.
* A running instance of the **Spring Boot Backend** at `http://localhost:8080`.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Azam0221/Python_Script_Archestra.git](https://github.com/Azam0221/Python_Script_Archestra.git)
    cd Safe_Agent
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Create venv
    python3 -m venv venv

    # Activate (Mac/Linux)
    source venv/bin/activate

    # Activate (Windows)
    venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

    > **Note:** If `requirements.txt` is missing, install the core packages manually:
    > `pip install uvicorn starlette httpx`

## Usage

1.  Ensure your Java Spring Boot backend is running on port `8080`.
2.  Start the Python Sentinel Bridge:

    ```bash
    python rogue_agent.py
    ```

3.  The server will start on:
    `http://0.0.0.0:9095`

## API Protocol

The bridge listens for **POST** requests containing JSON-RPC payloads.

### 1. Initialize
**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "initialize",
  "id": 1
}
