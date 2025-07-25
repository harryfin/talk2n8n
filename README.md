Danke für den Hinweis. Hier ist die überarbeitete Fassung der README, die klarstellt, dass je nach Umgebung eine entsprechende `.env.[env]`-Datei erforderlich ist:

---

# Voice-Controlled n8n Integration

## Overview

This Python package provides seamless integration of speech recognition into your n8n workflows.
It functions as a voice-activated assistant that listens for spoken commands, triggers corresponding n8n workflows, and responds using speech synthesis.

---

## Features

* Integration with n8n via webhooks
* Support for multiple speech recognition engines
* Workflow execution through voice commands
* Speech synthesis for audible responses

---

## Installation

### Prerequisites

#### On Linux

Install PortAudio (required for audio input/output):

```bash
sudo apt-get install portaudio19-dev
```

#### On Windows

Install the [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

---

## Configuration

Create an environment-specific `.env` file in the project root directory, depending on the environment you are running:

* `.env.dev` for development
* `.env.prod` for production

The file should include the following variables:

```env
WEBHOOK_URL=https://your-n8n-instance/webhook/your-workflow
ACTIVATION_PHRASE="Hallo Assistant"
ASSISTANT_NAME="My Assistant"
```

* `WEBHOOK_URL`: The n8n webhook endpoint that will be triggered
* `ACTIVATION_PHRASE`: The phrase that activates the assistant
* `ASSISTANT_NAME`: The name the assistant will respond to

---

## Usage

```bash
uv run main.py --app_env=dev   # Uses .env.dev
uv run main.py --app_env=prod  # Uses .env.prod
uv run main.py --help          # Show available options
```

---

## License

This project is licensed under the MIT License.
See the [LICENSE](./LICENSE) file for details.
