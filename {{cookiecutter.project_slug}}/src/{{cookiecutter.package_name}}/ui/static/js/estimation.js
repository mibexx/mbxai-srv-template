const { createApp } = Vue;

createApp({
  delimiters: ['[[', ']]'],
  data() {
    return {
      isLoading: false,
      helloResult: null,
      helloForm: {
        name: '',
        message: '',
        greetingStyle: 'casual',
        avatar: '',
        includeTime: false,
        savePreferences: false,
        emailNotification: false
      },
      autoSaveKey: 'hello-form-data'
    }
  },
  
  computed: {
    isFormValid() {
      return this.helloForm.name.trim().length > 0;
    }
  },
  
  mounted() {
    // Load saved form data on mount
    this.loadFormData();
    
    // Auto-save form data when it changes
    this.$watch('helloForm', () => {
      this.autoSaveFormData();
    }, { deep: true });
  },
  
  methods: {
    /**
     * Submit hello form
     */
    async submitHello() {
      if (!this.isFormValid) {
        ToastManager.error('Please enter your name');
        return;
      }
      
      this.isLoading = true;
      this.helloResult = null;
      
      try {
        // Use CeleryTaskTracker for task submission with progress tracking
        const result = await CeleryTaskTracker.submitTask(
          '/api/hello',
          this.helloForm,
          {
            onProgress: (status) => {
              console.log('Task progress:', status);
              // You can update UI with progress here if backend supports it
            },
            onSuccess: (data) => {
              this.helloResult = data;
              ToastManager.success('Greeting sent successfully!');
            },
            onError: (error) => {
              this.helloResult = { error };
              ToastManager.error('Failed to send greeting');
            }
          }
        );
        
      } catch (error) {
        console.error('Error submitting hello:', error);
        this.helloResult = { 
          error: 'Network error occurred. Please try again.' 
        };
        ToastManager.error('Network error occurred');
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Copy hello result to clipboard
     */
    async copyhelloResult() {
      if (!this.helloResult) return;
      
      try {
        const textToCopy = this.formatResultsForCopy();
        await navigator.clipboard.writeText(textToCopy);
        ToastManager.success('Result copied to clipboard!');
      } catch (error) {
        console.error('Failed to copy to clipboard:', error);
        ToastManager.error('Failed to copy to clipboard');
      }
    },

    /**
     * Format results for copying
     */
    formatResultsForCopy() {
      if (!this.helloResult) return '';
      
      if (this.helloResult.message) {
        return `Hello World Result: ${this.helloResult.message}`;
      } else if (this.helloResult.error) {
        return `Error: ${this.helloResult.error}`;
      }
      
      return 'No result available';
    },

    /**
     * Auto-save form data to localStorage
     */
    autoSaveFormData() {
      if (this.helloForm.savePreferences) {
        StorageHelper.save(this.autoSaveKey, this.helloForm);
      }
    },
    
    /**
     * Load form data from localStorage
     */
    loadFormData() {
      const savedData = StorageHelper.load(this.autoSaveKey);
      if (savedData && savedData.savePreferences) {
        this.helloForm = { ...this.helloForm, ...savedData };
      }
    },
    
    /**
     * Clear saved form data
     */
    clearFormData() {
      StorageHelper.remove(this.autoSaveKey);
      ToastManager.info('Saved preferences cleared');
    }
  }
}).mount('#estimation-app');
