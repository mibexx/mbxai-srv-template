# UI Components Guide

This guide provides comprehensive documentation for all UI components, helpers, and utilities available in this template.

## Table of Contents

1. [Getting Started](#getting-started)
2. [CSS Styles](#css-styles)
3. [JavaScript Helpers](#javascript-helpers)
4. [Form Components](#form-components)
5. [Toast Notifications](#toast-notifications)
6. [Progress Bars](#progress-bars)
7. [Status Badges](#status-badges)
8. [Celery Task Tracking](#celery-task-tracking)
9. [LocalStorage Management](#localstorage-management)
10. [Preview Page](#preview-page)

## Getting Started

### File Structure

```
ui/
├── static/
│   ├── css/
│   │   └── styles.css          # All component styles
│   └── js/
│       ├── helpers.js           # Utility helpers
│       ├── estimation.js        # Main app logic
│       └── components-preview.js # Preview page logic
├── templates/
│   ├── base.html                # Base template
│   ├── index.html               # Home page
│   ├── components-preview.html  # Components showcase
│   └── tasks/
│       └── hello.html           # Example task template
└── app.py                       # Flask application
```

### Including Files in Templates

In your Jinja templates, include the helpers and your app scripts:

```html
{% raw %}{% block scripts %}
<script src="{{ url_for('static', filename='js/helpers.js') }}"></script>
<script src="{{ url_for('static', filename='js/your-app.js') }}"></script>
{% endblock %}{% endraw %}
```

## CSS Styles

All styles are located in `static/css/styles.css` and use Tailwind CSS utilities.

### Button Classes

```html
<!-- Primary Button -->
<button class="btn-primary">Primary Action</button>

<!-- Secondary Button -->
<button class="btn-secondary">Secondary Action</button>

<!-- Success Button -->
<button class="btn-success">Success Action</button>

<!-- Danger Button -->
<button class="btn-danger">Danger Action</button>

<!-- Warning Button -->
<button class="btn-warning">Warning Action</button>

<!-- Info Button -->
<button class="btn-info">Info Action</button>
```

### Form Containers

```html
<div class="form-container">
  <div class="form-header">
    <h2>Form Title</h2>
    <p>Form description</p>
  </div>
  <div class="form-body">
    <!-- Form content -->
  </div>
</div>
```

### Content Sections

```html
<div class="content-section">
  <div class="content-section-header">
    <h2 class="content-section-title">Section Title</h2>
    <p class="content-section-subtitle">Section description</p>
  </div>
  <div class="content-section-body">
    <!-- Section content -->
  </div>
  <div class="content-section-footer">
    <!-- Footer actions -->
  </div>
</div>
```

## JavaScript Helpers

### StorageHelper

Manage localStorage with ease:

```javascript
// Save data
StorageHelper.save('myKey', { name: 'John', age: 30 });

// Load data
const data = StorageHelper.load('myKey', { default: 'value' });

// Check if exists
if (StorageHelper.exists('myKey')) {
  console.log('Key exists!');
}

// Remove data
StorageHelper.remove('myKey');

// Clear all
StorageHelper.clear();

// Get all keys
const keys = StorageHelper.keys();
```

### Auto-save Form Data

```javascript
// In your Vue component
mounted() {
  // Load saved data
  const savedData = StorageHelper.load('my-form-key');
  if (savedData) {
    this.formData = { ...this.formData, ...savedData };
  }
  
  // Auto-save on changes
  this.$watch('formData', () => {
    StorageHelper.save('my-form-key', this.formData);
  }, { deep: true });
}
```

## Form Components

### Text Input

```html
<div class="form-group">
  <label for="name" class="form-label">Name <span class="text-red-500">*</span></label>
  <input 
    v-model="formData.name" 
    type="text" 
    id="name" 
    placeholder="Enter your name"
    required>
  <p class="form-help">Helper text goes here</p>
</div>
```

### Textarea

```html
<div class="form-group">
  <label for="description" class="form-label">Description</label>
  <textarea 
    v-model="formData.description" 
    id="description" 
    rows="4"
    placeholder="Enter description..."></textarea>
  <p class="form-help">Provide additional details</p>
</div>
```

### Select Dropdown

```html
<div class="form-group">
  <label for="country" class="form-label">Country</label>
  <select v-model="formData.country" id="country">
    <option value="">Select a country...</option>
    <option value="us">United States</option>
    <option value="uk">United Kingdom</option>
  </select>
</div>
```

### File Upload

```html
<div class="form-group">
  <label for="document" class="form-label">Upload Document</label>
  <input 
    type="file" 
    id="document" 
    @change="handleFileUpload"
    accept=".pdf,.doc,.docx">
  <p class="form-help">Accepted formats: PDF, DOC, DOCX (Max 10MB)</p>
</div>
```

### Checkbox

```html
<div class="flex items-start">
  <div class="flex items-center h-5">
    <input 
      v-model="formData.newsletter" 
      type="checkbox" 
      id="newsletter"
      class="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500">
  </div>
  <div class="ml-3">
    <label for="newsletter" class="text-sm font-medium text-gray-900 cursor-pointer">
      Subscribe to newsletter
    </label>
    <p class="text-sm text-gray-600">Get weekly updates</p>
  </div>
</div>
```

### Radio Button

```html
<div class="flex items-start">
  <div class="flex items-center h-5">
    <input 
      v-model="formData.contactMethod" 
      type="radio" 
      id="contactEmail"
      value="email"
      class="h-4 w-4 text-indigo-600 border-gray-300 focus:ring-indigo-500">
  </div>
  <div class="ml-3">
    <label for="contactEmail" class="text-sm font-medium text-gray-900 cursor-pointer">
      Contact via Email
    </label>
  </div>
</div>
```

## Toast Notifications

### Using ToastManager

```javascript
// Show success toast
ToastManager.success('Operation completed successfully!');

// Show error toast
ToastManager.error('An error occurred');

// Show warning toast
ToastManager.warning('Please review your input');

// Show info toast
ToastManager.info('This is an informational message');

// Custom duration (0 = no auto-close)
ToastManager.show('Custom message', 'success', 10000); // 10 seconds
```

### Toast Types

- `success` - Green toast for successful operations
- `error` - Red toast for errors
- `warning` - Yellow toast for warnings
- `info` - Blue toast for information

## Progress Bars

### HTML Structure

```html
<div>
  <div class="flex justify-between mb-2">
    <span class="text-sm font-medium text-gray-700">Progress Label</span>
    <span class="text-sm font-medium text-gray-700">75%</span>
  </div>
  <div class="progress-container">
    <div class="progress-bar progress-bar-success" style="width: 75%"></div>
  </div>
</div>
```

### Progress Bar Types

```html
<!-- Success (Green) -->
<div class="progress-bar progress-bar-success" style="width: 75%"></div>

<!-- Info (Blue) -->
<div class="progress-bar progress-bar-info" style="width: 50%"></div>

<!-- Warning (Yellow) -->
<div class="progress-bar progress-bar-warning" style="width: 30%"></div>

<!-- Danger (Red) -->
<div class="progress-bar progress-bar-danger" style="width: 10%"></div>

<!-- Animated -->
<div class="progress-bar progress-bar-info progress-bar-animated" style="width: 50%"></div>
```

## Status Badges

### Usage

```html
<!-- Pending -->
<span class="status-badge status-badge-pending">Pending</span>

<!-- Processing -->
<span class="status-badge status-badge-processing">
  <svg class="w-3 h-3 mr-1 animate-spin" fill="none" viewBox="0 0 24 24">
    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
  </svg>
  Processing
</span>

<!-- Success -->
<span class="status-badge status-badge-success">Success</span>

<!-- Error -->
<span class="status-badge status-badge-error">Error</span>

<!-- Warning -->
<span class="status-badge status-badge-warning">Warning</span>
```

## Celery Task Tracking

### Basic Usage

```javascript
// Submit a task and track its progress
const result = await CeleryTaskTracker.submitTask(
  '/api/your-endpoint',
  { data: 'your data' },
  {
    onProgress: (status) => {
      console.log('Progress:', status.progress);
      console.log('Message:', status.message);
    },
    onSuccess: (result) => {
      console.log('Task completed:', result);
      ToastManager.success('Task completed successfully!');
    },
    onError: (error) => {
      console.error('Task failed:', error);
      ToastManager.error('Task failed: ' + error);
    },
    onComplete: (result) => {
      console.log('Task finished (success or failure)');
    }
  }
);
```

### Track Existing Task

```javascript
// Track a task by ID
CeleryTaskTracker.trackTask('task-id-123', {
  onProgress: (status) => {
    // Update UI with progress
    this.taskStatus = status.state;
    this.taskProgress = status.progress || 0;
  },
  onSuccess: (result) => {
    this.taskResult = result;
  }
});
```

### Configuration

```javascript
// Change polling interval (default: 1000ms)
CeleryTaskTracker.pollInterval = 2000; // Poll every 2 seconds

// Change max retries (default: 300)
CeleryTaskTracker.maxRetries = 600; // 10 minutes with 1s interval
```

## LocalStorage Management

### Form Auto-save Example

```javascript
data() {
  return {
    formData: {
      name: '',
      email: ''
    },
    autoSaveKey: 'my-form-data'
  }
},

mounted() {
  // Load saved data
  this.loadFormData();
  
  // Auto-save on changes
  this.$watch('formData', () => {
    StorageHelper.save(this.autoSaveKey, this.formData);
  }, { deep: true });
},

methods: {
  loadFormData() {
    const savedData = StorageHelper.load(this.autoSaveKey);
    if (savedData) {
      this.formData = { ...this.formData, ...savedData };
      ToastManager.info('Form data loaded');
    }
  },
  
  clearFormData() {
    StorageHelper.remove(this.autoSaveKey);
    this.formData = { name: '', email: '' };
    ToastManager.warning('Form data cleared');
  }
}
```

## Preview Page

Visit `/preview` to see all components in action. This page demonstrates:

- Toast notifications (all types)
- Progress bars (with animations)
- Status badges
- Comprehensive form with all field types
- Content sections
- LocalStorage integration

### Running the Preview

```bash
# Start the UI server
uv run python -m {{cookiecutter.package_name}}.ui.run

# Or use the template command
uv run template

# Visit http://localhost:5001/preview
```

## Best Practices

### 1. Form Validation

Always validate forms before submission:

```javascript
validateForm() {
  if (!FormValidator.isValidEmail(this.formData.email)) {
    ToastManager.error('Invalid email address');
    return false;
  }
  
  if (!FormValidator.minLength(this.formData.name, 2)) {
    ToastManager.error('Name must be at least 2 characters');
    return false;
  }
  
  return true;
}
```

### 2. Loading States

Show loading states during async operations:

```javascript
async submitForm() {
  this.isLoading = true;
  try {
    const result = await this.apiCall();
    ToastManager.success('Form submitted!');
  } catch (error) {
    ToastManager.error('Submission failed');
  } finally {
    this.isLoading = false;
  }
}
```

### 3. Error Handling

Always provide user feedback:

```javascript
try {
  await someOperation();
  ToastManager.success('Operation successful');
} catch (error) {
  console.error('Error:', error);
  ToastManager.error(error.message || 'Operation failed');
}
```

### 4. Accessibility

- Use proper labels for form fields
- Include helper text for complex inputs
- Mark required fields with `*`
- Use semantic HTML elements
- Ensure keyboard navigation works

## Customization

### Changing Theme Colors

Edit `static/css/styles.css` and modify the Tailwind classes:

```css
/* Change primary color from indigo to blue */
.btn-primary {
  @apply bg-blue-600 hover:bg-blue-700 focus:ring-blue-500;
}
```

### Adding New Components

1. Add styles to `styles.css`
2. Create reusable template in `templates/`
3. Add JavaScript logic if needed
4. Document in this README

## Troubleshooting

### Toast not showing

Make sure `helpers.js` is loaded before your app script:

```html
<script src="{{ url_for('static', filename='js/helpers.js') }}"></script>
<script src="{{ url_for('static', filename='js/your-app.js') }}"></script>
```

### LocalStorage not working

Check browser console for errors and ensure:
- Browser supports localStorage
- Not in private/incognito mode
- No browser extensions blocking it

### Styles not applying

Ensure CSS file is loaded:

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}" />
```

## Support

For issues or questions:
1. Check this documentation
2. Review the preview page (`/preview`)
3. Examine example code in `estimation.js` and `components-preview.js`

## License

This template is part of the {{cookiecutter.project_name}} project.

