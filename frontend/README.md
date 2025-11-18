# Sumble Advanced Query API - Frontend Demo

A simple, minimalist web interface to test and visualize the Sumble Advanced Query API.

## Features

- ✨ **Clean, Modern UI** - Gradient design with smooth animations
- 🎯 **Pre-loaded Examples** - 5 example queries ready to test
- ✏️ **Live Query Editor** - Edit JSON queries directly
- 📊 **Visual Results** - See job results and performance metrics
- ⚡ **Real-time Stats** - Response time and job count display
- 📱 **Responsive Design** - Works on desktop and mobile

## Quick Start

### 1. Make Sure API is Running

```bash
# From project root
docker compose up -d

# Verify API is running
curl http://localhost:8000/api/v1/health
```

### 2. Open the Frontend

**Option A: Direct File Open**
```bash
# Open in your default browser
open frontend/index.html

# Or on Linux
xdg-open frontend/index.html
```

**Option B: Simple HTTP Server (Recommended)**
```bash
# Python 3
cd frontend
python3 -m http.server 3000

# Then open: http://localhost:3000
```

**Option C: VS Code Live Server**
- Right-click `frontend/index.html`
- Select "Open with Live Server"

## Using the Frontend

### 1. Example Queries

Click any of the 5 pre-loaded examples:
- **Query 1**: Apple + .NET
- **Query 2**: NOT Apple AND (Statistician OR PSQL)
- **Query 3**: Python Jobs
- **Query 4**: (Google OR Microsoft) AND Python
- **Query 5**: Amazon AND (AWS OR Cloud) AND Engineer

### 2. Edit Query

Modify the JSON in the editor to create custom queries:

```json
{
  "type": "operator",
  "operator": "AND",
  "children": [
    {
      "type": "condition",
      "condition": {
        "field": "organization",
        "value": "google"
      }
    },
    {
      "type": "condition",
      "condition": {
        "field": "technology",
        "value": "python"
      }
    }
  ]
}
```

### 3. Adjust Result Limit

Change the "Result Limit" input (1-100) to control how many jobs are returned.

### 4. Execute Query

Click "🚀 Execute Query" or press `Ctrl/Cmd + Enter` in the editor.

### 5. View Results

Results display:
- ✅ Success/Error message
- 📊 Job count and response time
- 📋 List of matching jobs with IDs and dates

## Query Structure Reference

### Single Condition
```json
{
  "type": "condition",
  "condition": {
    "field": "technology",
    "value": "python"
  }
}
```

### AND Operator
```json
{
  "type": "operator",
  "operator": "AND",
  "children": [
    { /* condition 1 */ },
    { /* condition 2 */ }
  ]
}
```

### OR Operator
```json
{
  "type": "operator",
  "operator": "OR",
  "children": [
    { /* condition 1 */ },
    { /* condition 2 */ }
  ]
}
```

### NOT Operator
```json
{
  "type": "operator",
  "operator": "NOT",
  "children": [
    { /* condition to negate */ }
  ]
}
```

### Searchable Fields
- `organization` - Company name (e.g., "apple", "google")
- `technology` - Technology/stack (e.g., "python", ".net")
- `job_function` - Job role (e.g., "engineer", "data scientist")

## Troubleshooting

### API Connection Failed

**Error**: "Make sure the API is running on http://localhost:8000"

**Solution**:
```bash
# Check if API is running
docker compose ps

# If not running, start it
docker compose up -d

# Check health
curl http://localhost:8000/api/v1/health
```

### CORS Issues

If you see CORS errors in browser console:

1. The API already has CORS enabled for all origins
2. Make sure you're accessing the frontend via HTTP (not file://)
3. Use a simple HTTP server (see Quick Start above)

### Blank Results

If queries return 0 results:
- Check the search values (case-insensitive partial matching)
- Try example queries first to verify connection
- Verify data exists: Open pgAdmin4 and query the database

## Technical Details

### Stack
- **Pure HTML/CSS/JS** - No build tools or dependencies
- **Vanilla JavaScript** - No frameworks required
- **Fetch API** - Modern async HTTP requests
- **CSS Grid & Flexbox** - Responsive layout

### API Endpoint
- **URL**: http://localhost:8000/api/v1/jobs/search
- **Method**: POST
- **Body**: JSON query object
- **Query Param**: `?limit=10` (optional, default 10)

### Performance
- Queries typically complete in 50-500ms
- Response time displayed in real-time
- Frontend adds minimal overhead (<10ms)

## Customization

### Change API URL

Edit line in `index.html`:
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

### Change Theme Colors

Modify CSS variables at top of `<style>` section:
```css
/* Primary gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Accent color */
color: #667eea;
```

### Add More Examples

Add to the `examples` object in JavaScript:
```javascript
const examples = {
    // ... existing examples
    6: {
        "type": "condition",
        "condition": {"field": "technology", "value": "react"}
    }
};
```

Then add button in HTML:
```html
<button class="example-btn" onclick="loadExample(6)">
    <span class="example-title">Your Query Title</span>
    <span class="example-desc">Description</span>
</button>
```

## Files

- `index.html` - Complete single-file frontend (HTML + CSS + JS)
- `README.md` - This file

## Notes

- ✅ **Completely optional** - Main API works independently
- ✅ **No build required** - Open HTML file directly
- ✅ **No dependencies** - Pure vanilla JavaScript
- ✅ **Self-contained** - Everything in one HTML file
- ✅ **Production-ready** - Can be hosted on any static server

## Alternative Access

If you prefer command-line:
```bash
# Use curl
curl -X POST http://localhost:8000/api/v1/jobs/search \
  -H "Content-Type: application/json" \
  -d '{"type":"condition","condition":{"field":"technology","value":"python"}}'

# Or interactive docs
open http://localhost:8000/docs
```

---

**Enjoy exploring the API!** 🚀

