# 🎵 Music Request System

Let users request artists to be added to your music library!

---

## 📖 Overview

The Request System allows users to:
- 🔍 **Search** for artists
- ➕ **Request** artists to be added
- 🔐 **Authenticate** with Jellyfin/Emby/Plex
- ⭐ **Simple** - just username and password

Admins can:
- 📊 **Review** requests before adding
- 🎯 **Control** which artists get monitored
- 🔑 **Manage** authentication securely
- 📝 **Track** who requested what

---

## 🚀 Quick Setup

### **Step 1: Get Jellyfin API Key**

1. Login to Jellyfin as admin
2. Dashboard → Advanced → API Keys
3. Click "+ New API Key"
4. Name: `Blissful`
5. **Copy the key** (you'll need it)

### **Step 2: Configure Blissful**

1. Open Blissful: `http://localhost:7373`
2. Go to **Requests** tab
3. Enable **Music Request System**
4. Enable **Jellyfin Authentication**
5. Enter configuration:
   ```
   Jellyfin URL: https://jellyfin.example.com
   Jellyfin API Key: [paste your key]
   ```
6. Click **Save All Settings**

### **Step 3: Test Authentication**

1. Open request page: `http://localhost:7373/request`
2. Click **Login with Jellyfin**
3. Enter any Jellyfin user credentials
4. Should see: ✅ "Login successful!"

---

## 🔐 Authentication Methods

### **Jellyfin Authentication**

**How it works:**
```
User → Username + Password → Blissful
Blissful → Admin API Key → Jellyfin
Jellyfin → Validates User → Returns Token
User → Authenticated! ✅
```

**Configuration:**
```json
{
  "enable_jellyfin": true,
  "jellyfin_url": "https://jellyfin.example.com",
  "jellyfin_api_key": "admin-api-key-here"
}
```

**Benefits:**
- ✅ Users don't need API keys
- ✅ Admin controls access
- ✅ Secure authentication
- ✅ Existing user accounts

### **Emby Authentication**

Same as Jellyfin:

```json
{
  "enable_emby": true,
  "emby_url": "https://emby.example.com",
  "emby_api_key": "admin-api-key-here"
}
```

**Note:** Emby and Jellyfin can be enabled simultaneously!

### **Plex Authentication**

**How it works:**
```
User → Username + Password → Plex.tv
Plex.tv → Validates → Returns Token
User → Authenticated! ✅
```

**Configuration:**
```json
{
  "enable_plex": true
}
```

**Benefits:**
- ✅ No API key needed
- ✅ Works with any Plex account
- ✅ Simple setup

---

## 🎯 User Experience

### **Login Flow**

1. **User opens** request page
2. **Sees** authentication options
3. **Clicks** "Login with Jellyfin" (or Emby/Plex)
4. **Modal opens** with simple form:
   ```
   Username: [________]
   Password: [________]
   
   [Login] [Cancel]
   ```
5. **User enters** their credentials
6. **Authenticated!** ✅

### **Requesting Artists**

1. **Search** for artist:
   ```
   Search: [Metallica]  [🔍 Search]
   ```

2. **Results appear** with artist cards:
   ```
   ┌─────────────────────────────┐
   │  [Artist Image]             │
   │  Metallica                  │
   │  Heavy Metal • 25 albums    │
   │  [➕ Request Artist]        │
   └─────────────────────────────┘
   ```

3. **Click** "Request Artist"

4. **Artist added** to Lidarr (unmonitored)

5. **Success notification** appears:
   ```
   ✅ Metallica has been requested!
   ```

---

## ⚙️ Request Settings

### **Auto-Monitor**

Control if requested artists are automatically monitored:

```json
{
  "auto_monitor_requests": false
}
```

**Options:**
- **`false`** - Add unmonitored (admin approval needed)
- **`true`** - Add monitored (auto-download albums)

**Recommendation:** Start with `false` for control

### **Request Limits**

**Not yet implemented** - coming soon!

Future features:
- Max requests per user per day
- Request cooldown period
- Admin approval workflow

---

## 👥 Multi-User Setup

### **Scenario: Family Server**

**Users:**
- Dad, Mom, Kids

**Setup:**
1. Enable Jellyfin auth
2. Each family member has Jellyfin account
3. They can request artists
4. Dad (admin) reviews and approves

### **Scenario: Friend Group**

**Users:**
- 5-10 friends sharing server

**Setup:**
1. Enable Plex auth (easiest)
2. Friends use existing Plex accounts
3. Everyone can request
4. Admin batch-approves popular requests

### **Scenario: Public Server**

**Users:**
- Many users, some unknown

**Setup:**
1. Enable request limits (when available)
2. Require approval for all requests
3. Monitor for abuse
4. Remove inactive users periodically

---

## 🔒 Security Best Practices

### **API Key Management**

✅ **Do:**
- Generate dedicated API key for Blissful
- Store in `config.json` (not in code)
- Don't commit to version control
- Rotate keys periodically

❌ **Don't:**
- Share API keys
- Use admin user API key if possible
- Commit keys to Git
- Post keys in support requests

### **User Authentication**

✅ **Do:**
- Use strong passwords
- Enable 2FA on Jellyfin/Emby/Plex
- Monitor login attempts
- Review user list regularly

❌ **Don't:**
- Share passwords
- Use default accounts
- Allow weak passwords
- Ignore failed login attempts

### **Access Control**

✅ **Do:**
- Review requests before approving
- Remove inactive users
- Monitor disk usage
- Set up notifications

❌ **Don't:**
- Auto-approve all requests
- Allow unlimited requests
- Ignore unusual activity
- Share admin credentials

---

## 📊 Monitoring Requests

### **Viewing Requests**

Currently, requests are added directly to Lidarr.

**To see requests:**
1. Open Lidarr
2. Go to Artist list
3. Filter by "Unmonitored"
4. These are pending requests

### **Approving Requests**

In Lidarr:
1. Select artist
2. Click "Monitor"
3. Choose albums to download
4. Lidarr will start searching

### **Rejecting Requests**

In Lidarr:
1. Select artist
2. Click "Delete"
3. Confirm deletion
4. Artist removed

---

## 🎓 Advanced Configuration

### **Multiple Authentication**

Enable multiple methods:

```json
{
  "enable_jellyfin": true,
  "jellyfin_url": "https://jellyfin.example.com",
  "jellyfin_api_key": "key1",
  
  "enable_emby": true,
  "emby_url": "https://emby.example.com",
  "emby_api_key": "key2",
  
  "enable_plex": true
}
```

Users see all three options and can choose!

### **Custom Branding**

**Not yet implemented** - coming soon!

Future: Customize request page:
- Logo
- Colors
- Welcome message
- Rules/guidelines

### **Webhooks**

**Not yet implemented** - coming soon!

Future: Get notified of new requests:
- Discord webhook
- Slack notification
- Email alerts
- Custom webhooks

---

## 🐛 Troubleshooting

### **"API key not configured"**

**Solution:**
1. Check API key is in settings
2. Verify it's not empty
3. Make sure you clicked "Save"
4. Restart Blissful

### **"Invalid username or password"**

**Solutions:**
- ✅ Verify credentials work in Jellyfin directly
- ✅ Check for typos (passwords are case-sensitive)
- ✅ Make sure user account exists
- ✅ Try with different user
- ✅ Check Jellyfin logs for details

### **"Cannot connect to server"**

**Solutions:**
- ✅ Verify Jellyfin/Emby URL is correct
- ✅ Make sure server is running
- ✅ Check network connectivity
- ✅ Try accessing URL in browser
- ✅ Check firewall settings

### **Login button doesn't appear**

**Solutions:**
1. Check request system is enabled
2. Verify at least one auth method is enabled
3. Check browser console for errors (F12)
4. Hard refresh page (Ctrl+F5)

### **Requests not appearing in Lidarr**

**Solutions:**
- ✅ Check Lidarr connection is working
- ✅ Verify API key is correct
- ✅ Look in Lidarr activity log
- ✅ Check Blissful logs for errors
- ✅ Try adding artist manually to test

---

## 📝 Request Workflow

### **Complete Flow**

```
1. User Authentication
   ↓
2. Search for Artist
   ↓
3. Click "Request Artist"
   ↓
4. Blissful → Lidarr API
   ↓
5. Artist added (unmonitored)
   ↓
6. Admin reviews in Lidarr
   ↓
7. Admin enables monitoring
   ↓
8. Lidarr searches for albums
   ↓
9. Albums downloaded
   ↓
10. User happy! 🎵
```

### **Typical Timeline**

- **Request:** Instant
- **Admin Review:** Hours to days
- **Album Search:** Minutes
- **Download:** Minutes to hours
- **Total:** Same day to few days

---

## 💡 Tips & Tricks

### **For Admins**

1. **Batch Approve** - Review requests weekly
2. **Popular Artists** - Auto-approve well-known artists
3. **Quality Check** - Ensure good metadata before approving
4. **Communicate** - Let users know approval timeline

### **For Users**

1. **Be Patient** - Requests need approval
2. **Be Specific** - Use correct artist names
3. **Check First** - See if artist already exists
4. **Be Reasonable** - Don't request obscure/unavailable artists

### **Optimization**

1. **Disk Space** - Monitor available space
2. **Quality** - Set quality profiles in Lidarr
3. **Limits** - Set request limits if needed
4. **Cleanup** - Remove old unmonitored artists

---

## 🎉 Success Stories

### **Example: Home Server**

> "My family loves the request system! They search for artists on their phones, request them, and I approve during my morning coffee. Simple!" - John D.

### **Example: Friend Group**

> "We have 8 friends sharing a server. The request system means I don't get constant messages asking for music. They just request it themselves!" - Sarah M.

### **Example: Small Community**

> "Running a small private server for 20 friends. Request system with Plex auth made it super easy. No manual account management!" - Alex K.

---

## 📚 Related Guides

- **[Getting Started](#!/documentation?doc=getting-started)** - Initial setup
- **[Configuration](#!/documentation?doc=configuration)** - Advanced settings
- **[Troubleshooting](#!/documentation?doc=troubleshooting)** - Common issues

---

## 🔮 Coming Soon

Features in development:

- 🎯 Request approval workflow
- 📊 Request statistics
- 🔔 Webhook notifications
- 👥 User management interface
- 📱 Mobile-optimized interface
- 🎨 Custom branding

---

**Happy requesting!** 🎵
