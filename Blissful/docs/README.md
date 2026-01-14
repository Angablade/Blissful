# 🎵 Blissful - Lidarr Music Downloader

Welcome to **Blissful**, your intelligent music downloader and request system for Lidarr!

---

## 📸 Screenshots & Videos

### 🎬 See Blissful in Action

<table>
  <tr>
    <td align="center" width="50%">
      <h4>🎵 Full Interface Demo</h4>
      <a href="../promo/blissful.mp4">
        <img src="https://img.shields.io/badge/▶️-Watch_Video-6366f1?style=for-the-badge" alt="Watch Demo">
      </a>
      <br>
      <i>Complete walkthrough of all features</i>
    </td>
    <td align="center" width="50%">
      <h4>🔗 Lidarr Integration</h4>
      <a href="../promo/lidarr.mp4">
        <img src="https://img.shields.io/badge/▶️-Watch_Video-6366f1?style=for-the-badge" alt="Watch Demo">
      </a>
      <br>
      <i>Seamless integration with Lidarr</i>
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <h4>🎯 Drag & Drop Sources</h4>
      <a href="../promo/draganddrop.mp4">
        <img src="https://img.shields.io/badge/▶️-Watch_Video-6366f1?style=for-the-badge" alt="Watch Demo">
      </a>
      <br>
      <i>Easy source priority management</i>
    </td>
    <td align="center" width="50%">
      <h4>🎵 Request System</h4>
      <img src="../promo/requestspage.png" alt="Request System" width="90%">
      <br>
      <i>Beautiful request page interface</i>
    </td>
  </tr>
</table>

---

## 📖 What is Blissful?

Blissful is a powerful microservice that bridges the gap between your music library (Lidarr) and various download sources. It enables:

- 🎵 **Automated Music Downloads** - Download tracks from YouTube, SoundCloud, and 1000+ sources
- 🎯 **Music Request System** - Let users request artists via Jellyfin/Emby authentication
- 🔄 **Lidarr Integration** - Seamless integration with your existing Lidarr setup
- 🎨 **User-Friendly Interface** - Clean web interface for configuration and management
- 🔌 **Browser Extension** - Userscript for downloading directly from Lidarr

---

## ✨ Key Features

### **For Administrators:**
- ⚙️ Easy configuration through web interface
- 🔑 Secure authentication with Jellyfin/Emby/Plex
- 📊 Source management (1000+ supported sites)
- 🎚️ Quality control (format, bitrate, conversion)
- 🗂️ Path mapping for remote servers
- 🐳 Docker support included

### **For Users:**
- 🎵 Request artists to be added to library
- 🔍 Search across music platforms
- 📱 Simple authentication (username + password)
- 🎉 No API keys required for users

### **Technical Features:**
- 🏗️ Modular architecture (easy to maintain)
- 🔒 Secure (admin API keys, user authentication)
- 🚀 Fast (yt-dlp powered downloads)
- 🎵 High quality (configurable audio formats)
- 🔄 Auto-conversion (MP3, FLAC, M4A, etc.)

---

## 🚀 Quick Start

### **1. Installation**

```bash
# Clone the repository
git clone https://github.com/angablade/blissful.git
cd blissful

# Install dependencies
pip install -r requirements.txt

# Start the application
python run.py
```

### **2. Configure Lidarr**

1. Open Blissful: `http://localhost:7373`
2. Go to **Lidarr** tab
3. Enter your Lidarr URL and API key
4. Click **Test Connection**

### **3. Enable Requests (Optional)**

1. Go to **Requests** tab
2. Enable **Music Request System**
3. Configure Jellyfin/Emby authentication
4. Save settings

### **4. Download Music**

**Option A - Via Userscript:**
1. Go to **Userscript** tab
2. Download and install the userscript
3. Visit your Lidarr album page
4. Click **Download Missing Tracks**

**Option B - Via API:**
```bash
curl -X POST http://localhost:7373/api/download-track \
  -H "Content-Type: application/json" \
  -d '{"artist": "Metallica", "title": "Enter Sandman"}'
```

---

## 📚 Documentation

| Guide | Description |
|-------|-------------|
| **[Getting Started](#!/documentation?doc=getting-started)** | Installation, setup, and first steps |
| **[Configuration](#!/documentation?doc=configuration)** | Detailed configuration guide |
| **[Request System](#!/documentation?doc=request-system)** | Setting up music requests |
| **[Troubleshooting](#!/documentation?doc=troubleshooting)** | Common issues and solutions |

---

## 🎯 Use Cases

### **Scenario 1: Home Server**
You run Lidarr at home and want to fill missing tracks from your collection:
- Configure Blissful with your Lidarr setup
- Install the userscript
- One-click download missing tracks

### **Scenario 2: Multi-User Setup**
You have multiple users accessing your Plex/Jellyfin server:
- Enable the request system
- Users can request artists
- Artists are added to Lidarr (unmonitored for approval)

### **Scenario 3: Remote Server**
Your Lidarr runs on a remote server:
- Configure path mapping
- Downloads are automatically placed in correct folders
- Lidarr picks them up immediately

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│              Web Interface                      │
│  (Configuration, Requests, Management)          │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│          Blissful Core (Flask)                  │
│  ┌───────────┐  ┌───────────┐  ┌────────────┐ │
│  │ Auth      │  │ Request   │  │  Download  │ │
│  │ Manager   │  │ Manager   │  │  Manager   │ │
│  └───────────┘  └───────────┘  └────────────┘ │
└─────────────────┬───────────────────────────────┘
                  │
    ┌─────────────┼─────────────┬─────────────┐
    │             │             │             │
┌───▼────┐  ┌────▼─────┐  ┌───▼──────┐  ┌──▼──────┐
│Lidarr  │  │yt-dlp    │  │Jellyfin/ │  │Sources  │
│API     │  │(1000+    │  │Emby/Plex │  │(YouTube,│
│        │  │sources)  │  │Auth      │  │etc)     │
└────────┘  └──────────┘  └──────────┘  └─────────┘
```

---

## 🔧 Requirements

### **System Requirements:**
- Python 3.8 or higher
- 2GB RAM minimum
- 10GB disk space (for downloads)
- Internet connection

### **Software Requirements:**
- Lidarr (v1.0+)
- FFmpeg (for audio conversion)
- yt-dlp (installed automatically)

### **Optional:**
- Docker & Docker Compose
- Jellyfin/Emby/Plex (for request system)
- Web browser with userscript support

---

## 🐳 Docker Deployment

```bash
# Using Docker Compose
docker-compose up -d

# Manual Docker
docker build -t blissful .
docker run -d -p 7373:7373 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/downloads:/app/downloads \
  blissful
```

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. 🐛 **Report bugs** - Open an issue with details
2. 💡 **Suggest features** - Share your ideas
3. 📝 **Improve docs** - Help make them better
4. 🔧 **Submit PRs** - Fix bugs or add features

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Credits

**Created by:** Angablade  
**Documentation by:** Synthia

### **Built With:**
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Download engine
- [FFmpeg](https://ffmpeg.org/) - Audio conversion
- [Lidarr](https://lidarr.audio/) - Music library management

---

## 📞 Support

Need help? Here's where to get support:

- 📖 **Documentation** - Check other guides in this tab
- 🐛 **Issues** - GitHub Issues for bug reports
- 💬 **Discussions** - GitHub Discussions for questions
- 📧 **Email** - Contact the developer

---

## 🎉 Thank You!

Thank you for using Blissful! We hope it makes managing your music library easier and more enjoyable.

**Happy listening!** 🎵

---

*Last updated: January 2026*
