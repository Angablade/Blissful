# ⚙️ Configuration Guide

Complete guide to configuring Blissful for your needs.

---

## 🎯 Configuration Overview

Blissful has several configuration tabs:

| Tab | Purpose |
|-----|---------|
| **Lidarr** | Connect to your Lidarr instance |
| **Downloads** | Configure download settings |
| **Paths** | Set up path mapping |
| **Sources** | Manage download sources |
| **Requests** | Configure user request system |
| **Userscript** | Download browser extension |
| **Tools** | System utilities and tests |

---

## 🔗 Lidarr Configuration

### **Basic Settings**

```json
{
  "lidarr_url": "http://localhost:8686",
  "lidarr_api_key": "your-api-key-here"
}
```

#### **Finding Your API Key**

1. Open Lidarr web interface
2. Go to: Settings → General
3. Scroll to **Security** section
4. Copy the **API Key**

#### **Testing Connection**

Click **Test Connection** to verify:
- ✅ Lidarr is reachable
- ✅ API key is valid
- ✅ Version is compatible

### **Advanced Settings**

#### **Root Folders**

Lidarr root folders are detected automatically:
- Click **Get Root Folders**
- Select primary folder for downloads
- Used for path construction

#### **Quality Profile**

Default quality profile for new artists:
- Select from dropdown
- Used when adding via requests
- Can be changed later in Lidarr

---

## ⬇️ Download Configuration

### **Output Format**

Choose audio format for downloads:

| Format | Quality | Compatibility | File Size |
|--------|---------|---------------|-----------|
| **MP3** | Good | Excellent | Medium |
| **FLAC** | Lossless | Good | Large |
| **M4A** | Good | Excellent | Medium |
| **OGG** | Good | Fair | Small |
| **OPUS** | Excellent | Fair | Small |

**Recommendation:** MP3 for compatibility, FLAC for audiophiles

### **Quality/Bitrate**

| Bitrate | Quality | Use Case |
|---------|---------|----------|
| **128k** | Acceptable | Mobile, streaming |
| **192k** | Good | General listening |
| **256k** | Very Good | Home audio |
| **320k** | Excellent | High-quality audio |
| **V0** | Variable | Smart compression |

**Recommendation:** 320k for best quality, 192k for balanced

### **Download Location**

```
Default: ./downloads/
```

Options:
- **Relative path:** `downloads/` (relative to Blissful)
- **Absolute path:** `/home/user/music/` (full path)

Files are organized as:
```
downloads/
  └── Artist Name/
      └── Album Name/
          ├── 01 - Track Title.mp3
          ├── 02 - Track Title.mp3
          └── ...
```

### **Conversion Settings**

#### **Sample Rate**
- **44100 Hz** - CD quality (recommended)
- **48000 Hz** - Studio quality
- **96000 Hz** - High-resolution

#### **Channels**
- **Stereo (2)** - Standard (recommended)
- **Mono (1)** - Save space
- **Surround** - Multi-channel audio

---

## 🗺️ Path Mapping

Path mapping translates local paths to remote paths.

### **When to Use Path Mapping**

Use path mapping when:
- ✅ Blissful runs on different machine than Lidarr
- ✅ Using Docker with bind mounts
- ✅ Network shares with different mount points
- ✅ Windows ↔ Linux path differences

### **Example Scenarios**

#### **Scenario 1: Docker**

**Blissful sees:**
```
/app/downloads/Artist/Album/track.mp3
```

**Lidarr sees:**
```
/music/Artist/Album/track.mp3
```

**Mapping:**
```
Blissful Path: /app/downloads
Lidarr Path: /music
```

#### **Scenario 2: Network Share**

**Blissful (Windows):**
```
\\server\music\Artist\Album\track.mp3
```

**Lidarr (Linux):**
```
/mnt/music/Artist/Album/track.mp3
```

**Mapping:**
```
Blissful Path: \\server\music
Lidarr Path: /mnt/music
```

#### **Scenario 3: Remote Server**

**Blissful (Local):**
```
D:\Blissful\downloads\Artist\Album\track.mp3
```

**Lidarr (Remote):**
```
/home/user/media/music/Artist/Album/track.mp3
```

**Mapping:**
```
Blissful Path: D:\Blissful\downloads
Lidarr Path: /home/user/media/music
```

### **Adding Path Mappings**

1. Go to **Paths** tab
2. Click **Add Mapping**
3. Enter:
   - **Blissful Path:** Path on Blissful server
   - **Lidarr Path:** Path on Lidarr server
4. Click **Save**

### **Testing Path Mapping**

```
Test Input: D:\Blissful\downloads\Metallica\Metallica\01 - Enter Sandman.mp3
Expected Output: /music/Metallica/Metallica/01 - Enter Sandman.mp3
```

---

## 🌐 Source Configuration

### **Source Priorities**

Control which sources are tried first:

1. **Drag and drop** to reorder
2. **Top sources** are tried first
3. **Disabled sources** are skipped

### **Source Categories**

| Category | Examples | Quality | Speed |
|----------|----------|---------|-------|
| **Music Services** | Spotify, Deezer, SoundCloud | Excellent | Fast |
| **Video Platforms** | YouTube, Vimeo | Good | Fast |
| **Podcasts** | Apple Podcasts, Spotify | Good | Medium |
| **Archives** | Internet Archive | Variable | Slow |
| **Free Music** | Jamendo, Free Music Archive | Good | Fast |

### **Recommended Source Order**

1. **SoundCloud** - High quality, reliable
2. **YouTube Music** - Large library, good quality
3. **YouTube** - Fallback, always available
4. **Bandcamp** - High quality, artist-friendly
5. **Spotify** - Premium quality (requires account)

### **Filtering Sources**

- **By Category:** Show only music services
- **By Tier:** Filter by reliability (1-4)
- **By Search:** Find specific sources

---

## 🎵 Request System Configuration

### **Enabling Requests**

1. Go to **Requests** tab
2. Check **Enable Music Request System**
3. Configure authentication method(s)
4. Save settings

### **Jellyfin Authentication**

#### **Step 1: Get API Key**

```bash
# In Jellyfin web interface:
Dashboard → Advanced → API Keys → New API Key
Name: "Blissful"
Copy the generated key
```

#### **Step 2: Configure Blissful**

```json
{
  "enable_jellyfin": true,
  "jellyfin_url": "https://jellyfin.example.com",
  "jellyfin_api_key": "your-jellyfin-api-key"
}
```

#### **Step 3: Test**

1. Open: `http://localhost:7373/request`
2. Click "Login with Jellyfin"
3. Enter any Jellyfin user credentials
4. Should authenticate successfully ✅

### **Emby Authentication**

Same as Jellyfin:

```json
{
  "enable_emby": true,
  "emby_url": "https://emby.example.com",
  "emby_api_key": "your-emby-api-key"
}
```

### **Plex Authentication**

Simpler setup (uses Plex.tv):

```json
{
  "enable_plex": true
}
```

No API key needed! Users authenticate directly with Plex.

### **Request Settings**

#### **Auto-Monitor**

```json
{
  "auto_monitor_requests": false
}
```

- **false** - Artists added unmonitored (admin approval)
- **true** - Artists automatically monitored (auto-download)

#### **Request Notifications**

Configure webhooks for new requests:

```json
{
  "webhook_url": "https://discord.com/api/webhooks/..."
}
```

---

## 🔧 Advanced Configuration

### **Environment Variables**

Override settings with environment variables:

```bash
export BLISSFUL_PORT=7373
export BLISSFUL_HOST=0.0.0.0
export BLISSFUL_DEBUG=false
export LIDARR_URL=http://localhost:8686
export LIDARR_API_KEY=your-key
```

### **config.json**

Manual configuration file:

```json
{
  "lidarr_url": "http://localhost:8686",
  "lidarr_api_key": "your-api-key",
  "output_format": "mp3",
  "quality": "320k",
  "download_path": "./downloads/",
  "enable_requests": true,
  "enable_jellyfin": true,
  "jellyfin_url": "https://jellyfin.example.com",
  "jellyfin_api_key": "jellyfin-api-key",
  "lidarr_path_mapping": {
    "/app/downloads": "/music"
  },
  "source_priorities": [
    "soundcloud",
    "youtube-music",
    "youtube",
    "bandcamp"
  ]
}
```

### **Docker Environment**

```yaml
# docker-compose.yml
environment:
  - LIDARR_URL=http://lidarr:8686
  - LIDARR_API_KEY=${LIDARR_API_KEY}
  - JELLYFIN_URL=http://jellyfin:8096
  - JELLYFIN_API_KEY=${JELLYFIN_API_KEY}
volumes:
  - ./config:/app/config
  - ./downloads:/app/downloads
  - /path/to/music:/music
```

---

## 🔍 Configuration Best Practices

### **Security**

✅ **Do:**
- Keep API keys secret
- Use environment variables for sensitive data
- Don't commit `config.json` to version control
- Rotate API keys regularly

❌ **Don't:**
- Share API keys publicly
- Use default passwords
- Expose Blissful to internet without auth

### **Performance**

✅ **Do:**
- Use SSD for downloads
- Enable only needed sources
- Set appropriate quality for your needs
- Use path mapping efficiently

❌ **Don't:**
- Enable all sources
- Use unnecessarily high quality
- Download to slow network drives

### **Organization**

✅ **Do:**
- Use consistent path mapping
- Let Lidarr handle organization
- Keep config backed up
- Document custom settings

❌ **Don't:**
- Manually move downloaded files
- Mix different quality settings
- Change settings frequently

---

## 🎓 Configuration Templates

### **Home Server (Basic)**

```json
{
  "lidarr_url": "http://localhost:8686",
  "lidarr_api_key": "your-key",
  "output_format": "mp3",
  "quality": "320k"
}
```

### **Multi-User (Requests)**

```json
{
  "enable_requests": true,
  "enable_jellyfin": true,
  "jellyfin_url": "https://jellyfin.local",
  "jellyfin_api_key": "your-key",
  "auto_monitor_requests": false
}
```

### **Remote Server (Docker)**

```json
{
  "lidarr_url": "http://lidarr:8686",
  "lidarr_path_mapping": {
    "/app/downloads": "/music"
  }
}
```

### **Audiophile (High Quality)**

```json
{
  "output_format": "flac",
  "quality": "best",
  "sample_rate": 96000
}
```

---

## 📝 Configuration Checklist

Before going live:

- [ ] Lidarr connection tested
- [ ] Download location configured
- [ ] Path mapping set up (if needed)
- [ ] Source priorities configured
- [ ] Request system enabled (if needed)
- [ ] Authentication tested (if using requests)
- [ ] Userscript installed
- [ ] Test download completed successfully

---

**Next:** [Request System Guide](#!/documentation?doc=request-system)
