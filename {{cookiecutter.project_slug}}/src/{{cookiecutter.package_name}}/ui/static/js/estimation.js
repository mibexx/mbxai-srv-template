const { createApp } = Vue;

createApp({
  delimiters: ['[[', ']]'],
  data() {
    return {
      isLoading: false,
      helloResult: null,
      helloForm: {
        name: ''
      }
    }
  },
  computed: {
    isFormValid() {
      return this.helloForm.name.trim().length > 0;
    }
  },
  methods: {
    async submitHello() {
      if (!this.isFormValid) return;
      
      this.isLoading = true;
      this.helloResult = null;
      
      try {
        const response = await fetch('/api/hello', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(this.helloForm)
        });
        
        const data = await response.json();
        
        if (response.ok) {
          // Success case - API returns {message: "Hello, Name!", name: "Name"}
          this.helloResult = data;
          this.showFlashMessage('Greeting sent successfully!', 'success');
        } else {
          // Error case
          this.helloResult = { 
            error: data.detail || data.error || 'An error occurred' 
          };
          this.showFlashMessage('Failed to send greeting', 'error');
        }
      } catch (error) {
        console.error('Error submitting hello:', error);
        this.helloResult = { 
          error: 'Network error occurred. Please try again.' 
        };
        this.showFlashMessage('Network error occurred', 'error');
      } finally {
        this.isLoading = false;
      }
    },

    async copyhelloResult() {
      if (!this.helloResult) return;
      
      try {
        const textToCopy = this.formatResultsForCopy();
        await navigator.clipboard.writeText(textToCopy);
        this.showFlashMessage('Result copied to clipboard!', 'success');
      } catch (error) {
        console.error('Failed to copy to clipboard:', error);
        this.showFlashMessage('Failed to copy to clipboard', 'error');
      }
    },

    formatResultsForCopy() {
      if (!this.helloResult) return '';
      
      if (this.helloResult.message) {
        return `Hello World Result: ${this.helloResult.message}`;
      } else if (this.helloResult.error) {
        return `Error: ${this.helloResult.error}`;
      }
      
      return 'No result available';
    },

    showFlashMessage(message, category) {
      // Create a temporary flash message element
      const flashDiv = document.createElement('div');
      flashDiv.className = `fixed top-4 right-4 z-50 rounded-md p-4 mb-2 shadow-lg ${
        category === 'error' 
          ? 'bg-red-50 border border-red-200 text-red-700' 
          : category === 'success' 
          ? 'bg-green-50 border border-green-200 text-green-700' 
          : 'bg-blue-50 border border-blue-200 text-blue-700'
      }`;
      
      flashDiv.innerHTML = `
        <div class="flex items-center">
          <div class="flex-shrink-0">
            ${category === 'error' 
              ? '<svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414-1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" /></svg>'
              : '<svg class="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" /></svg>'
            }
          </div>
          <div class="ml-3">
            <p class="text-sm font-medium">${message}</p>
          </div>
          <div class="ml-auto pl-3">
            <button onclick="this.parentElement.parentElement.parentElement.remove()" class="inline-flex text-gray-400 hover:text-gray-600">
              <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      `;
      
      document.body.appendChild(flashDiv);
      
      // Auto-remove the message after 5 seconds
      setTimeout(() => {
        if (flashDiv.parentNode) {
          flashDiv.parentNode.removeChild(flashDiv);
        }
      }, 5000);
    }
  }
}).mount('#estimation-app');
