# Troubleshooting Guide

## If you don't see CSS/design changes after restarting:

### 1. Hard Refresh Your Browser
The browser may have cached the old CSS files. Try:

**Chrome/Edge (Windows/Linux):**
- Press `Ctrl + Shift + R` or `Ctrl + F5`

**Chrome/Edge (Mac):**
- Press `Cmd + Shift + R`

**Firefox:**
- Press `Ctrl + Shift + R` (Windows/Linux) or `Cmd + Shift + R` (Mac)

**Safari:**
- Press `Cmd + Option + R`

### 2. Clear Browser Cache
1. Open browser settings
2. Clear browsing data/cache
3. Select "Cached images and files"
4. Clear data
5. Refresh the page

### 3. Check Flask is Running in Debug Mode
Make sure your `app.py` has `debug=True`:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

### 4. Verify Static Files
Check that these files exist:
- `static/css/style.css`
- `static/js/main.js`

### 5. Check Browser Console
1. Open Developer Tools (F12)
2. Go to Console tab
3. Look for any errors loading CSS/JS files
4. Go to Network tab and check if CSS/JS files are loading (status 200)

### 6. Restart Flask Server
1. Stop the server (Ctrl+C)
2. Start it again:
```bash
python app.py
```

### 7. Check File Permissions
Make sure files are readable:
```bash
chmod 644 static/css/style.css
chmod 644 static/js/main.js
```

## If images are not showing:

1. Run the reprocess script to fix image URLs:
```bash
python reprocess_posts.py
```

2. Check that images are loading from Blogger CDN (they should work if the original blog is accessible)

## If code syntax highlighting is not working:

1. Check browser console for Prism.js errors
2. Verify internet connection (Prism.js loads from CDN)
3. Check that code blocks have proper language classes

