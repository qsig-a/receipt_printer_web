# Receipt Printer Web Interface

A lightweight Flask web application that serves as a portal to send text messages to a remote receipt printer via a webhook. It is designed to integrate with automation platforms like Home Assistant and includes a logging system backed by Google Firestore.

## Features

- **Print Portal**: A clean, mobile-friendly interface to send messages, protected by an access key.
- **Admin History**: A secured dashboard to view print logs (timestamp, IP, status, message).
- **Data Management**: Options to download logs as CSV or clear the history.
- **Cloud Ready**: Optimized for Google Cloud Run with native Firestore integration.

## Prerequisites

- Python 3.9+
- A Google Cloud Project with Firestore enabled (Native mode).
- A webhook URL (e.g., Home Assistant Nabu Casa URL) that accepts a JSON payload: `{"message": "your text"}`.

## Installation

1. Clone the repository.
2. Install the required dependencies:
   ```bash
   pip install flask requests google-cloud-firestore signalwire==2.1.1
   ```

## Configuration

The application is configured using environment variables. You can set these in your local environment or your cloud provider's configuration settings.

| Variable | Description | Default |
|----------|-------------|---------|
| `WEBHOOK_URL` | The destination URL for print requests. | `https://hooks.nabucasa.com/...` |
| `ACCESS_PASSWORD` | The keycode required to send a message. | `password` |
| `ADMIN_PASSWORD` | The password required to view logs. | `adminpassword` |
| `PORT` | The port the web server listens on. | `5000` |
| `CHARACTER_LIMIT` | Optional integer limit for message length. | `None` |

### SignalWire Configuration (SMS Support)

To enable the SMS feature, you must provide the following:

| Variable | Description |
|----------|-------------|
| `SIGNALWIRE_PROJECT_ID` | Your SignalWire Project ID. |
| `SIGNALWIRE_TOKEN` | Your SignalWire API Token. |
| `SIGNALWIRE_SPACE_URL` | Your SignalWire Space URL (e.g., `example.signalwire.com`). |
| `SIGNALWIRE_FROM_NUMBER` | The phone number owned by your SignalWire project. |

## Running Locally

1. **Authentication**: If running outside of Google Cloud, you must set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to point to your service account JSON key.

2. **Start the App**:
   ```bash
   python app.py
   ```

3. Open your browser to `http://localhost:5000`.

## Running with Docker

1. **Build the image**:
   ```bash
   docker build -t receipt-printer .
   ```

2. **Run the container**:
   ```bash
   docker run -p 5000:5000 \
     -e WEBHOOK_URL="YOUR_WEBHOOK_URL" \
     -v /path/to/service-account.json:/app/credentials.json \
     -e GOOGLE_APPLICATION_CREDENTIALS="/app/credentials.json" \
     receipt-printer
   ```

## Deployment

This application is designed to run on **Google Cloud Run**:

1. Build the container or deploy directly from source.
2. Set the environment variables listed above during deployment.
3. The application uses the default service account to authenticate with Firestore (ensure the service account has `Cloud Datastore User` role).

### GitHub Actions

This repository includes a workflow to auto-deploy to Cloud Run. Configure these secrets in your repo settings:

- `GCP_PROJECT_ID`: Your Google Cloud Project ID.
- `GCP_CREDENTIALS`: Service Account JSON key.
- `WEBHOOK_URL`, `ACCESS_PASSWORD`, `ADMIN_PASSWORD`: App configuration.