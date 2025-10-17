/**
 * Custom Select Component - Vue 3
 * A fully styled dropdown that matches input field styling perfectly
 */

const CustomSelect = {
  name: 'CustomSelect',
  props: {
    modelValue: {
      type: [String, Number],
      default: ''
    },
    options: {
      type: Array,
      required: true,
      // Expected format: [{ value: 'us', label: 'United States' }, ...]
    },
    placeholder: {
      type: String,
      default: 'Select an option...'
    },
    disabled: {
      type: Boolean,
      default: false
    },
    required: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      isOpen: false
    }
  },
  computed: {
    selectedOption() {
      return this.options.find(opt => opt.value === this.modelValue);
    },
    displayText() {
      return this.selectedOption ? this.selectedOption.label : this.placeholder;
    }
  },
  methods: {
    toggle() {
      if (!this.disabled) {
        this.isOpen = !this.isOpen;
      }
    },
    selectOption(option) {
      this.$emit('update:modelValue', option.value);
      this.isOpen = false;
    },
    handleClickOutside(event) {
      if (!this.$el.contains(event.target)) {
        this.isOpen = false;
      }
    }
  },
  mounted() {
    document.addEventListener('click', this.handleClickOutside);
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside);
  },
  template: `
    <div class="custom-select-wrapper" :class="{ 'custom-select-disabled': disabled }">
      <button
        type="button"
        @click="toggle"
        :disabled="disabled"
        class="custom-select-button"
        :class="{ 
          'custom-select-open': isOpen,
          'custom-select-has-value': modelValue
        }"
      >
        <span :class="{ 'text-gray-500': !modelValue }">{{ "{{" }} displayText {{ "}}" }}</span>
        <svg 
          class="custom-select-arrow" 
          :class="{ 'custom-select-arrow-open': isOpen }"
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      
      <transition name="custom-select-dropdown">
        <div v-if="isOpen" class="custom-select-dropdown">
          <div 
            v-for="option in options" 
            :key="option.value"
            @click="selectOption(option)"
            class="custom-select-option"
            :class="{ 'custom-select-option-selected': option.value === modelValue }"
          >
            {{ "{{" }} option.label {{ "}}" }}
          </div>
        </div>
      </transition>
    </div>
  `
};

// Make it available globally
if (typeof window !== 'undefined') {
  window.CustomSelect = CustomSelect;
}
