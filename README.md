# stagedings

![Status: Active](https://img.shields.io/badge/status-active-brightgreen)
[![Backend: FastAPI](https://img.shields.io/badge/backend-FastAPI-blue)](https://fastapi.tiangolo.com/)
[![Real-time: WebSockets](https://img.shields.io/badge/real--time-WebSockets-orange)](https://fastapi.tiangolo.com/advanced/websockets/)
[![Protocol: OSC](https://img.shields.io/badge/protocol-OSC-purple)](http://opensoundcontrol.org/)
[![Control: MIDI](https://img.shields.io/badge/control-MIDI-yellow)](https://www.midi.org/specifications-old/item/table-1-summary-of-midi-message)
[![OpenAPI Spec](https://img.shields.io/badge/OpenAPI-available-brightgreen)](https://swagger.io/specification/)
![Clients: Multiple](https://img.shields.io/badge/clients-multiple-lightgrey)

### **stagedings** is the next-generation web UI and API to navigate scenes and subscenes in [mididings](https://github.com/mididings/mididings)
> 🚧 **NOTE: This project is scheduled to be moved to the [mididings](https://github.com/mididings) GitHub organization.**  
> Please star or watch the repo to stay updated on the move.

---
> ⚠️ **Important:**  
> stagedings requires a **mididings scene patch dictionary** defined in the `run` section of your mididings script to work correctly.  
> See the mididings documentation on the [`run` section here](https://mididings.github.io/mididings/main.html#mididings.run) for how to structure your patch.

> ⚠️ **Note for legacy mididings users:**  
> stagedings is designed to **replace the old `livedings` UI**, which was based on Tkinter.  
> It offers a modern, web-based interface with enhanced flexibility and real-time control capabilities.
 
## 📸 UI Preview

A responsive, real-time interface for scene/subscene navigation in mididings.

<img src="docs/stagedings-ui.png" alt="stagedings UI screenshot" width="700"/>


---

## 🚀 Features

- Web UI with real-time scene/subscene updates
- FastAPI backend with full REST and WebSocket support
- Multiple clients supported
- Use the mididings OSC interface
- It exposes a **fully compliant OpenAPI spec** for easy generation of SDK clients in any language, enabling flexible remote control of mididings.

---

### The UI interface allow
* Direct navigation through scenes and subscenes
* Exposes the Restart, Panic, Query and Quit commands

### The REST API expose
* Endoints for direct navigation through scenes and subscenes
* Endoints to the Restart, Panic, Query and Quit commands

### Dependencies 
* mididings community
* liblo
* pyliblo
* fastapi

### 💬 Feedback & Contributions
We welcome bug reports, feature ideas, and contributions! Please open an issue or discussion.

### 📜 License
All files in this repository are released under the terms of the GNU
General Public License as published by the Free Software Foundation;
either version 2 of the License, or (at your option) any later version.

For more details, please read the LICENSE file.