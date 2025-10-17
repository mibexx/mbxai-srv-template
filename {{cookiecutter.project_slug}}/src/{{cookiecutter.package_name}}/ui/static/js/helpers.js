/**
 * UI Helper Functions
 * Provides utilities for localStorage management, toast notifications, and Celery task tracking
 */

// ============================================================================
// LocalStorage Helpers
// ============================================================================

const StorageHelper = {
  /**
   * Save data to localStorage
   * @param {string} key - The key to store data under
   * @param {any} value - The value to store (will be JSON stringified)
   * @returns {boolean} - Success status
   */
  save(key, value) {
    try {
      const serialized = JSON.stringify(value);
      localStorage.setItem(key, serialized);
      return true;
    } catch (error) {
      console.error('Error saving to localStorage:', error);
      return false;
    }
  },

  /**
   * Load data from localStorage
   * @param {string} key - The key to retrieve data from
   * @param {any} defaultValue - Default value if key doesn't exist
   * @returns {any} - The stored value or default value
   */
  load(key, defaultValue = null) {
    try {
      const serialized = localStorage.getItem(key);
      if (serialized === null) {
        return defaultValue;
      }
      return JSON.parse(serialized);
    } catch (error) {
      console.error('Error loading from localStorage:', error);
      return defaultValue;
    }
  },

  /**
   * Remove data from localStorage
   * @param {string} key - The key to remove
   * @returns {boolean} - Success status
   */
  remove(key) {
    try {
      localStorage.removeItem(key);
      return true;
    } catch (error) {
      console.error('Error removing from localStorage:', error);
      return false;
    }
  },

  /**
   * Clear all localStorage data
   * @returns {boolean} - Success status
   */
  clear() {
    try {
      localStorage.clear();
      return true;
    } catch (error) {
      console.error('Error clearing localStorage:', error);
      return false;
    }
  },

  /**
   * Check if a key exists in localStorage
   * @param {string} key - The key to check
   * @returns {boolean} - True if key exists
   */
  exists(key) {
    return localStorage.getItem(key) !== null;
  },

  /**
   * Get all keys from localStorage
   * @returns {string[]} - Array of all keys
   */
  keys() {
    return Object.keys(localStorage);
  },

  /**
   * Auto-save form data on input change
   * @param {string} formId - The form element ID
   * @param {string} storageKey - The localStorage key to use
   */
  autoSaveForm(formId, storageKey) {
    const form = document.getElementById(formId);
    if (!form) {
      console.error(`Form with ID ${formId} not found`);
      return;
    }

    const saveFormData = () => {
      const formData = new FormData(form);
      const data = {};
      for (const [key, value] of formData.entries()) {
        data[key] = value;
      }
      this.save(storageKey, data);
    };

    form.addEventListener('input', saveFormData);
    form.addEventListener('change', saveFormData);
  },

  /**
   * Restore form data from localStorage
   * @param {string} formId - The form element ID
   * @param {string} storageKey - The localStorage key to use
   */
  restoreForm(formId, storageKey) {
    const form = document.getElementById(formId);
    if (!form) {
      console.error(`Form with ID ${formId} not found`);
      return;
    }

    const data = this.load(storageKey);
    if (!data) return;

    for (const [key, value] of Object.entries(data)) {
      const input = form.elements[key];
      if (input) {
        if (input.type === 'checkbox') {
          input.checked = value === 'on' || value === true;
        } else if (input.type === 'radio') {
          if (input.value === value) {
            input.checked = true;
          }
        } else {
          input.value = value;
        }
      }
    }
  }
};

// ============================================================================
// Toast Notification System
// ============================================================================

const ToastManager = {
  container: null,
  defaultDuration: 5000,

  /**
   * Initialize toast container
   */
  init() {
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.className = 'toast-container';
      document.body.appendChild(this.container);
    }
  },

  /**
   * Show a toast notification
   * @param {string} message - The message to display
   * @param {string} type - Toast type: success, error, warning, info
   * @param {number} duration - Duration in milliseconds (0 for no auto-close)
   * @returns {HTMLElement} - The toast element
   */
  show(message, type = 'info', duration = null) {
    this.init();

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const iconMap = {
      success: '<svg class="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" /></svg>',
      error: '<svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414-1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" /></svg>',
      warning: '<svg class="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" /></svg>',
      info: '<svg class="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" /></svg>'
    };

    toast.innerHTML = `
      <div class="flex items-center">
        <div class="flex-shrink-0">
          ${iconMap[type] || iconMap.info}
        </div>
        <div class="ml-3 flex-1">
          <p class="text-sm font-medium">${message}</p>
        </div>
        <div class="ml-3 flex-shrink-0">
          <button class="inline-flex text-gray-400 hover:text-gray-600 focus:outline-none">
            <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>
      </div>
    `;

    const closeBtn = toast.querySelector('button');
    closeBtn.addEventListener('click', () => this.remove(toast));

    this.container.appendChild(toast);

    // Auto-remove after duration
    const autoDuration = duration === null ? this.defaultDuration : duration;
    if (autoDuration > 0) {
      setTimeout(() => this.remove(toast), autoDuration);
    }

    return toast;
  },

  /**
   * Remove a toast
   * @param {HTMLElement} toast - The toast element to remove
   */
  remove(toast) {
    if (!toast || !toast.parentNode) return;
    
    toast.classList.add('toast-removing');
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 300);
  },

  /**
   * Show success toast
   */
  success(message, duration = null) {
    return this.show(message, 'success', duration);
  },

  /**
   * Show error toast
   */
  error(message, duration = null) {
    return this.show(message, 'error', duration);
  },

  /**
   * Show warning toast
   */
  warning(message, duration = null) {
    return this.show(message, 'warning', duration);
  },

  /**
   * Show info toast
   */
  info(message, duration = null) {
    return this.show(message, 'info', duration);
  }
};

// ============================================================================
// Celery Task Tracker
// ============================================================================

const CeleryTaskTracker = {
  activeTasks: new Map(),
  pollInterval: 1000, // 1 second
  maxRetries: 300, // 5 minutes total

  /**
   * Submit a task to the backend and track its progress
   * @param {string} endpoint - The API endpoint to call
   * @param {object} data - The data to send
   * @param {object} callbacks - Callback functions: onProgress, onSuccess, onError, onComplete
   * @returns {Promise} - Promise that resolves when task completes
   */
  async submitTask(endpoint, data, callbacks = {}) {
    const {
      onProgress = null,
      onSuccess = null,
      onError = null,
      onComplete = null
    } = callbacks;

    try {
      // Initial task submission
      if (onProgress) {
        onProgress({
          status: 'PENDING',
          progress: 0,
          message: 'Submitting task...'
        });
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Request failed' }));
        throw new Error(errorData.error || errorData.detail || 'Request failed');
      }

      const result = await response.json();

      // Check if response includes task_id for async tracking
      if (result.task_id) {
        return await this.trackTask(result.task_id, callbacks);
      }

      // Synchronous response - task completed immediately
      if (onSuccess) {
        onSuccess(result);
      }
      if (onComplete) {
        onComplete(result);
      }

      return result;

    } catch (error) {
      console.error('Task submission error:', error);
      if (onError) {
        onError(error.message || 'An error occurred');
      }
      if (onComplete) {
        onComplete(null);
      }
      throw error;
    }
  },

  /**
   * Track an existing task by ID
   * @param {string} taskId - The task ID to track
   * @param {object} callbacks - Callback functions
   * @returns {Promise} - Promise that resolves when task completes
   */
  async trackTask(taskId, callbacks = {}) {
    const {
      onProgress = null,
      onSuccess = null,
      onError = null,
      onComplete = null
    } = callbacks;

    return new Promise((resolve, reject) => {
      let retryCount = 0;

      const checkStatus = async () => {
        try {
          const response = await fetch(`/api/task/${taskId}/status`);
          const status = await response.json();

          // Update progress
          if (onProgress) {
            onProgress(status);
          }

          // Check task state
          if (status.state === 'SUCCESS') {
            if (onSuccess) {
              onSuccess(status.result);
            }
            if (onComplete) {
              onComplete(status.result);
            }
            this.activeTasks.delete(taskId);
            resolve(status.result);
            return;
          }

          if (status.state === 'FAILURE') {
            const errorMsg = status.result?.error || 'Task failed';
            if (onError) {
              onError(errorMsg);
            }
            if (onComplete) {
              onComplete(null);
            }
            this.activeTasks.delete(taskId);
            reject(new Error(errorMsg));
            return;
          }

          // Task still processing
          retryCount++;
          if (retryCount >= this.maxRetries) {
            const timeoutMsg = 'Task timeout - exceeded maximum wait time';
            if (onError) {
              onError(timeoutMsg);
            }
            if (onComplete) {
              onComplete(null);
            }
            this.activeTasks.delete(taskId);
            reject(new Error(timeoutMsg));
            return;
          }

          // Continue polling
          setTimeout(checkStatus, this.pollInterval);

        } catch (error) {
          console.error('Error checking task status:', error);
          retryCount++;
          
          if (retryCount >= this.maxRetries) {
            if (onError) {
              onError('Failed to check task status');
            }
            if (onComplete) {
              onComplete(null);
            }
            this.activeTasks.delete(taskId);
            reject(error);
          } else {
            setTimeout(checkStatus, this.pollInterval);
          }
        }
      };

      // Store task reference
      this.activeTasks.set(taskId, { callbacks, startTime: Date.now() });

      // Start polling
      checkStatus();
    });
  },

  /**
   * Cancel task tracking (doesn't cancel the actual task on backend)
   * @param {string} taskId - The task ID to stop tracking
   */
  cancelTracking(taskId) {
    this.activeTasks.delete(taskId);
  },

  /**
   * Get all active task IDs
   * @returns {string[]} - Array of active task IDs
   */
  getActiveTasks() {
    return Array.from(this.activeTasks.keys());
  }
};

// ============================================================================
// Form Validation Helper
// ============================================================================

const FormValidator = {
  /**
   * Validate email format
   */
  isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  },

  /**
   * Validate URL format
   */
  isValidUrl(url) {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  },

  /**
   * Check if string is not empty
   */
  isNotEmpty(value) {
    return value && value.trim().length > 0;
  },

  /**
   * Check minimum length
   */
  minLength(value, min) {
    return value && value.length >= min;
  },

  /**
   * Check maximum length
   */
  maxLength(value, max) {
    return value && value.length <= max;
  },

  /**
   * Validate number range
   */
  inRange(value, min, max) {
    const num = parseFloat(value);
    return !isNaN(num) && num >= min && num <= max;
  }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    StorageHelper,
    ToastManager,
    CeleryTaskTracker,
    FormValidator
  };
}

