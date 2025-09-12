# stagedings

[![Status: Active](https://img.shields.io/badge/status-active-brightgreen)](#stagedings)
[![Backend: FastAPI](https://img.shields.io/badge/backend-FastAPI-blue)](https://fastapi.tiangolo.com/)
[![Protocol: WebSockets](https://img.shields.io/badge/protocol-WebSockets-orange)](https://fastapi.tiangolo.com/advanced/websockets/)
[![Protocol: OSC](https://img.shields.io/badge/protocol-OSC-purple)](http://opensoundcontrol.org/)
[![Protocol: MIDI](https://img.shields.io/badge/protocol-MIDI-yellow)](https://www.midi.org/specifications-old/item/table-1-summary-of-midi-message)
[![OpenAPI Spec](https://img.shields.io/badge/OpenAPI-available-brightgreen)](https://swagger.io/specification/)
### **stagedings** is a modern API to navigate scenes and subscenes that has been configured in a [mididings](https://github.com/mididings/mididings) script

---
> 🤔 **Why stagedings?** 
> * It offers a modern, web-based interface with enhanced flexibility and real-time control capabilities
>   * It is an alternative of the legacy **`livedings UI`**, which was based on Tkinter 🪓
> * ⚙️ Adds a HTTP layer that facilitates control and navigation allowing the abstraction of OSC subcalls
>   * 🔥 That layer offers an Open API specification, so it is possible to generate a client SDK in multiple language with an Open Api Code generator like [Kiota](https://github.com/microsoft/kiota) making possible to control [mididings](https://github.com/mididings/mididings) in .NET, Go, Java, PHP, Python, Ruby and TypeScript using the openapi.json file available from the Swagger or ReDoc UI.
> * A **mididings scene patch dictionary** defined in the `run` section of a [mididings](https://github.com/mididings/mididings) script is required to work correctly
>   * 🗒️ See the [mididings](https://github.com/mididings/mididings) documentation on the [`run` section here](https://mididings.github.io/mididings/main.html#mididings.run) for how to structure your patch

## 📸 UI Preview

### A responsive, real-time interface for scene/subscene navigation in mididings

<img src="docs/stagedings-ui.png" alt="stagedings UI screenshot" width="700"/>

---
## 🚀 Features
- Web UI with real-time scene/subscene updates
- FastAPI backend with full REST and WebSocket support
- Multiple clients supported
- Use the mididings OSC interface
- It exposes a **fully compliant OpenAPI spec** for easy generation of SDK clients in any language, enabling flexible remote control of mididings

---

### The UI interface allow
* Direct navigation through scenes and subscenes
* Exposes the Restart, Panic, Query and Quit commands

### The REST API expose
* Endpoints for direct navigation through scenes and subscenes
* Endpoints to the Restart, Panic, Query and Quit commands

---

## ⚒️ Installation & dependencies
#### On the server running mididings with OSC support
* Clone this repository
* In the stagedings/src directory
  * Create a .env file
    * Add the key STAGEDINGS_WS_HOST with the server name and the port of your choice:
      * STAGEDINGS_WS_HOST=localhost:5000

#### In a Python Virtual Environment
* mididings community >= **20250818** with OSC support 
  * See the mididings README for build instructions
* pip install fastapi
* pip install jinja2
* pip install uvicorn\[standard\]
---
# ▶️ Running the application

* In the stagedings/src directory
  
  * uvicorn main:app --port 5000 --host 0.0.0.0

* Then navigate to http://localhost:5000
  
  * / for the menu
  * /ui for the frontend
  * /docs or /redoc for API documentation

## 📸 Documentation preview
### Swagger
<img src="docs/stagedings-swagger.png" alt="stagedings UI screenshot" width="800"/>

### ReDoc
<img src="docs/stagedings-redoc.png" alt="stagedings UI screenshot" width="800"/>

### 💬 Feedback & Contributions

We welcome bug reports, feature ideas, and contributions! Please open an issue or discussion

### 📜 License

All files in this repository are released under the terms of the GNU
General Public License as published by the Free Software Foundation;
either version 2 or later of the License.
