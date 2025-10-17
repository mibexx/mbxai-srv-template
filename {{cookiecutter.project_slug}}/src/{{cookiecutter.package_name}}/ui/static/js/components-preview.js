const { createApp } = Vue;

createApp({
  delimiters: ['[[', ']]'],
  data() {
    return {
      // Progress tracking
      progress: {
        success: 75,
        info: 45,
        warning: 30
      },
      
      // Form data
      formData: {
        firstName: '',
        lastName: '',
        email: '',
        phone: '',
        website: '',
        age: '',
        description: '',
        country: '',
        role: '',
        newsletter: false,
        marketing: false,
        terms: false,
        contactMethod: 'email'
      },
      
      formSubmitting: false,
      autoSaveKey: 'components-preview-form-data'
    }
  },
  
  mounted() {
    // Load saved form data on mount
    this.loadFormData();
    
    // Auto-save form data when it changes
    this.$watch('formData', () => {
      this.autoSaveFormData();
    }, { deep: true });
  },
  
  methods: {
    /**
     * Show toast notification
     */
    showToast(type) {
      const messages = {
        success: 'Operation completed successfully!',
        error: 'An error occurred while processing your request.',
        warning: 'Please review your input before proceeding.',
        info: 'This is an informational message.'
      };
      
      ToastManager.show(messages[type] || messages.info, type);
    },
    
    /**
     * Update progress bars
     */
    updateProgress() {
      this.progress.success = Math.min(100, this.progress.success + 10);
      this.progress.info = Math.min(100, this.progress.info + 15);
      this.progress.warning = Math.min(100, this.progress.warning + 20);
      
      if (this.progress.success >= 100 && this.progress.info >= 100 && this.progress.warning >= 100) {
        ToastManager.success('All progress bars completed!');
      }
    },
    
    /**
     * Reset progress bars
     */
    resetProgress() {
      this.progress.success = 0;
      this.progress.info = 0;
      this.progress.warning = 0;
      ToastManager.info('Progress bars reset');
    },
    
    /**
     * Handle file upload
     */
    handleFileUpload(event) {
      const file = event.target.files[0];
      if (file) {
        if (file.size > 10 * 1024 * 1024) {
          ToastManager.error('File size exceeds 10MB limit');
          event.target.value = '';
          return;
        }
        ToastManager.success(`File "${file.name}" selected (${(file.size / 1024).toFixed(2)} KB)`);
      }
    },
    
    /**
     * Submit form
     */
    async submitForm() {
      if (!this.validateForm()) {
        ToastManager.error('Please fill in all required fields');
        return;
      }
      
      this.formSubmitting = true;
      
      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        ToastManager.success('Form submitted successfully!');
        console.log('Form data:', this.formData);
        
        // Optionally clear form after submission
        // this.resetForm();
      } catch (error) {
        ToastManager.error('Failed to submit form. Please try again.');
        console.error('Form submission error:', error);
      } finally {
        this.formSubmitting = false;
      }
    },
    
    /**
     * Validate form
     */
    validateForm() {
      // Check required fields
      if (!this.formData.firstName || !this.formData.lastName || !this.formData.email) {
        return false;
      }
      
      if (!this.formData.country) {
        return false;
      }
      
      if (!this.formData.terms) {
        ToastManager.warning('You must agree to the terms and conditions');
        return false;
      }
      
      // Validate email format
      if (!FormValidator.isValidEmail(this.formData.email)) {
        ToastManager.error('Please enter a valid email address');
        return false;
      }
      
      // Validate website if provided
      if (this.formData.website && !FormValidator.isValidUrl(this.formData.website)) {
        ToastManager.error('Please enter a valid website URL');
        return false;
      }
      
      // Validate age if provided
      if (this.formData.age) {
        const age = parseInt(this.formData.age);
        if (age < 18 || age > 120) {
          ToastManager.error('Age must be between 18 and 120');
          return false;
        }
      }
      
      return true;
    },
    
    /**
     * Reset form
     */
    resetForm() {
      this.formData = {
        firstName: '',
        lastName: '',
        email: '',
        phone: '',
        website: '',
        age: '',
        description: '',
        country: '',
        role: '',
        newsletter: false,
        marketing: false,
        terms: false,
        contactMethod: 'email'
      };
      
      ToastManager.info('Form reset to default values');
    },
    
    /**
     * Auto-save form data to localStorage
     */
    autoSaveFormData() {
      StorageHelper.save(this.autoSaveKey, this.formData);
    },
    
    /**
     * Save form data manually
     */
    saveFormData() {
      StorageHelper.save(this.autoSaveKey, this.formData);
      ToastManager.success('Form data saved to localStorage');
    },
    
    /**
     * Load form data from localStorage
     */
    loadFormData() {
      const savedData = StorageHelper.load(this.autoSaveKey);
      if (savedData) {
        this.formData = { ...this.formData, ...savedData };
        ToastManager.info('Form data loaded from localStorage');
      }
    },
    
    /**
     * Clear saved form data
     */
    clearFormData() {
      StorageHelper.remove(this.autoSaveKey);
      this.resetForm();
      ToastManager.warning('Saved form data cleared');
    }
  }
}).mount('#components-app');

