# UI Components Quick Start Guide

## 🚀 Getting Started in 3 Steps

### 1. Start the UI Server

```bash
cd {{cookiecutter.project_slug}}

# Development mode (with auto-reload)
uv run uidev

# OR Production mode
uv run ui
```

### 2. Open Your Browser

Navigate to the components preview page:
```
http://localhost:5001/preview
```

### 3. Explore Components

The preview page shows:
- ✅ Toast notifications (click buttons to see them)
- ✅ Progress bars (with animations)
- ✅ Status badges
- ✅ Comprehensive forms (all field types)
- ✅ Container sections
- ✅ LocalStorage demo

## 📋 What's Available

### Components

| Component | Description | CSS Class |
|-----------|-------------|-----------|
| **Buttons** | 6 variants (primary, secondary, success, danger, warning, info) | `.btn-primary`, `.btn-secondary`, etc. |
| **Forms** | Text, email, password, number, tel, url, textarea, select, file, checkbox, radio | Auto-styled |
| **Containers** | Reusable content sections with header, body, footer | `.content-section` |
| **Toasts** | Non-intrusive notifications | `ToastManager.success()` |
| **Progress** | Animated progress bars | `.progress-bar` |
| **Badges** | Status indicators | `.status-badge-*` |

### JavaScript Helpers

| Helper | Purpose | Example |
|--------|---------|---------|
| **StorageHelper** | localStorage management | `StorageHelper.save('key', data)` |
| **ToastManager** | Show notifications | `ToastManager.success('Saved!')` |
| **CeleryTaskTracker** | Track async tasks | `CeleryTaskTracker.submitTask(...)` |
| **FormValidator** | Validate inputs | `FormValidator.isValidEmail(email)` |

## 💡 Quick Examples

### Show a Toast

```javascript
ToastManager.success('Data saved successfully!');
ToastManager.error('An error occurred');
ToastManager.warning('Please review your input');
ToastManager.info('Processing...');
```

### Save to LocalStorage

```javascript
// Save
StorageHelper.save('user-preferences', { theme: 'dark', lang: 'en' });

// Load
const prefs = StorageHelper.load('user-preferences', { theme: 'light' });

// Remove
StorageHelper.remove('user-preferences');
```

### Auto-save Form Data

```javascript
mounted() {
  // Load saved data
  const saved = StorageHelper.load('my-form');
  if (saved) this.formData = saved;
  
  // Auto-save on changes
  this.$watch('formData', () => {
    StorageHelper.save('my-form', this.formData);
  }, { deep: true });
}
```

### Track Celery Task

```javascript
const result = await CeleryTaskTracker.submitTask(
  '/api/process',
  { data: 'your data' },
  {
    onProgress: (status) => {
      console.log('Progress:', status.progress);
    },
    onSuccess: (result) => {
      ToastManager.success('Task completed!');
    },
    onError: (error) => {
      ToastManager.error('Task failed');
    }
  }
);
```

## 📦 Using Components in Your Templates

### 1. Include Required Scripts

```html
{% raw %}{% block scripts %}
<script src="{{ url_for('static', filename='js/helpers.js') }}"></script>
<script src="{{ url_for('static', filename='js/your-app.js') }}"></script>
{% endblock %}{% endraw %}
```

### 2. Use CSS Classes

```html
<!-- Button -->
<button class="btn-primary">Click Me</button>

<!-- Form Input -->
<div class="form-group">
  <label class="form-label">Name</label>
  <input type="text" placeholder="Enter name">
  <p class="form-help">Your full name</p>
</div>

<!-- Content Section -->
<div class="content-section">
  <div class="content-section-header">
    <h2 class="content-section-title">Title</h2>
  </div>
  <div class="content-section-body">
    Content goes here
  </div>
</div>
```

### 3. Use JavaScript Helpers

```javascript
const { createApp } = Vue;

createApp({
  mounted() {
    ToastManager.info('App loaded!');
  },
  methods: {
    async saveData() {
      StorageHelper.save('data', this.formData);
      ToastManager.success('Data saved!');
    }
  }
}).mount('#app');
```

## 🎨 Customization

### Change Theme Colors

Edit `static/css/styles.css`:

```css
.btn-primary {
  /* Change from indigo to blue */
  @apply bg-blue-600 hover:bg-blue-700 focus:ring-blue-500;
}
```

### Add New Toast Type

Edit `static/js/helpers.js`:

```javascript
// Add a new toast type
ToastManager.custom = function(message, duration = null) {
  return this.show(message, 'custom', duration);
};
```

## 📚 Full Documentation

For complete documentation, see:
- **UI Components README**: `UI_COMPONENTS_README.md`
- **Improvements Summary**: `UI_IMPROVEMENTS_SUMMARY.md`
- **Preview Page**: http://localhost:5001/preview

## 🔧 Troubleshooting

### Can't see the preview page?

1. Make sure the UI server is running: `uv run uidev`
2. Check the correct port (default: 5001)
3. Look for errors in terminal

### Toasts not showing?

Make sure `helpers.js` is loaded before your app script:
```html
<script src="{{ url_for('static', filename='js/helpers.js') }}"></script>
<script src="{{ url_for('static', filename='js/your-app.js') }}"></script>
```

### Styles not applying?

Check that CSS is linked in base.html:
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}" />
```

### LocalStorage not working?

- Check browser console for errors
- Ensure not in private/incognito mode
- Verify browser supports localStorage

## ✅ Next Steps

1. ✨ **Explore** the preview page at `/preview`
2. 📖 **Read** the full documentation in `UI_COMPONENTS_README.md`
3. 🎯 **Copy** examples from `components-preview.js`
4. 🚀 **Build** your amazing features!

---

**Need Help?**
- Check the preview page: http://localhost:5001/preview
- Review the examples: `static/js/components-preview.js`
- Read full docs: `UI_COMPONENTS_README.md`

Happy coding! 🎉

