# Sentinel Bridge (Agent Proxy)

**Sentinel Bridge** is a lightweight, asynchronous Python middleware built with **Starlette** and **Uvicorn**. It acts as a secure firewall between an Autonomous AI Agent (via Archestra) and your internal **Spring Boot** backend.

It implements a **JSON-RPC 2.0** style protocol (compatible with Model Context Protocol standards) to enforce permission controls, real-time logging, and a "kill switch" mechanism.

## Features

* **JSON-RPC Interface:** Handles standard MCP methods: `initialize`, `tools/list`, and `tools/call`.
* **Security Gating (The Kill Switch):** Checks the Java backend before *every single action* to verify if the agent is active. If the agent is "Killed," execution is blocked immediately.
* **Human-in-the-Loop:** Implements a polling loop for high-risk tools (like `request_permission`), pausing execution until an Admin physically approves the request via the Android App.
* **Async Logging:** Streams real-time agent activity logs (`EXECUTING`, `AUTH_REQUIRED`) directly to the Spring Boot API.
* **Tool Proxy:** securely forwards approved tool calls (like `deploy`, `status`) to the backend.

## Tech Stack

* **Python 3.10+**
* **Starlette** (ASGI Framework)
* **Uvicorn** (ASGI Server)
* **HTTPX** (Async HTTP Client)

## Prerequisites

1.  Python 3.8 or higher.
2.  A running instance of the **Sentinel Spring Boot Backend** at `http://localhost:8080`.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Azam0221/Python_Script_Archestra.git
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
    pip install uvicorn starlette httpx
    ```

## Configuration (Connecting to Archestra)

To make the AI Agent use this bridge, you must register it as an **MCP Server** in Archestra.

1.  Open **Archestra**.
2.  Go to **Settings** -> **MCP Gateways** (or Tool Registries).
3.  Click **"Add New Server"**.
4.  Enter the following details:
    * **Name:** `Sentinel-Bridge`
    * **URL:** `http://localhost:9095` (or `http://host.docker.internal:9095` if running in Docker).
    * **Type:** `SSE` (Server-Sent Events) or `HTTP` depending on your version.
5.  **Enable the Tools:** Go to your Agent's configuration and toggle "Sentinel-Bridge" tools to **ON**.

## Usage

1.  **Ensure Backend is Running:**
    Make sure your Spring Boot API is active on port `8080`.

2.  **Start the Bridge:**
    ```bash
    python bridge.py
    ```

    You should see:
    > 🚀 SENTINEL BRIDGE RUNNING on http://0.0.0.0:9095

## 🔌 API Protocol

The bridge listens for `POST` requests containing JSON-RPC payloads.

**Example 1: Initialize Handshake**
```json
{
  "jsonrpc": "2.0",
  "method": "initialize",
  "id": 1
}
