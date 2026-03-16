/**
 * @file app.js
 * @brief Resume Extractor Application JavaScript
 * @details Handles all client-side functionality including file uploads,
 *          sidebar toggling, dark/light theme switching, API communication,
 *          and UI updates.
 * @author Resume Extractor Team
 * @date 2024
 * @version 2.0.0
 */

/**
 * @class ResumeExtractorApp
 * @brief Main application class
 * @details Manages the entire application state and functionality
 */
class ResumeExtractorApp {
    constructor() {
        this.sidebarOpen = false;
        this.processingHistory = [];
        this.currentSection = 'upload';
        this.darkMode = document.documentElement.getAttribute('data-theme') === 'dark';
        this.init();
    }

    /**
     * @brief Initialize the application
     * @details Sets up event listeners and initializes UI components
     */
    init() {
        this.setupEventListeners();
        this.initDarkMode();
        this.loadSkillsCount();
        this.updateStats();
    }

    /**
     * @brief Set up all event listeners
     * @details Binds events for sidebar, file upload, navigation, etc.
     */
    setupEventListeners() {
        // Sidebar toggle
        const sidebarToggle = document.getElementById('sidebarToggle');
        const sidebar = document.getElementById('sidebar');

        sidebarToggle.addEventListener('click', () => {
            this.toggleSidebar();
        });

        // Close sidebar when clicking outside
        document.addEventListener('click', (e) => {
            if (this.sidebarOpen &&
                !sidebar.contains(e.target) &&
                !sidebarToggle.contains(e.target)) {
                this.closeSidebar();
            }
        });

        // File upload
        const fileInput = document.getElementById('fileInput');
        const uploadArea = document.getElementById('uploadArea');

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileUpload(e.target.files[0]);
            }
        });

        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');

            if (e.dataTransfer.files.length > 0) {
                const file = e.dataTransfer.files[0];
                if (this.isValidFileType(file.name)) {
                    this.handleFileUpload(file);
                } else {
                    this.showToast('Invalid file type', 'Please upload PDF, TXT, DOC, or DOCX files.', 'error');
                }
            }
        });

        // Navigation
        document.querySelectorAll('.nav-section a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = e.target.dataset.section;
                this.switchSection(section);
                this.closeSidebar();
            });
        });

        // Collapsible cards (click + keyboard Enter/Space for a11y)
        const rawTextHeader = document.getElementById('rawTextHeader');
        if (rawTextHeader) {
            rawTextHeader.addEventListener('click', () => {
                this.toggleCollapsible(rawTextHeader, 'rawTextContent');
            });
            rawTextHeader.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.toggleCollapsible(rawTextHeader, 'rawTextContent');
                }
            });
        }

        // Dark mode toggle button
        const darkModeToggle = document.getElementById('darkModeToggle');
        if (darkModeToggle) {
            darkModeToggle.addEventListener('click', () => this.toggleDarkMode());
        }

        // Upload area keyboard accessibility (reuses uploadArea from above)
        if (uploadArea) {
            uploadArea.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    document.getElementById('fileInput').click();
                }
            });
        }

        // Settings toggles
        const autoExtract = document.getElementById('autoExtract');
        const showConfidence = document.getElementById('showConfidence');

        if (autoExtract) {
            autoExtract.addEventListener('change', (e) => {
                localStorage.setItem('autoExtract', e.target.checked);
            });
            // Load saved preference
            autoExtract.checked = localStorage.getItem('autoExtract') !== 'false';
        }

        if (showConfidence) {
            showConfidence.addEventListener('change', (e) => {
                localStorage.setItem('showConfidence', e.target.checked);
                this.updateSkillsDisplay();
            });
            showConfidence.checked = localStorage.getItem('showConfidence') !== 'false';
        }
    }

    /**
     * @brief Toggle sidebar visibility
     */
    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        this.sidebarOpen = !this.sidebarOpen;

        if (this.sidebarOpen) {
            sidebar.classList.add('open');
        } else {
            sidebar.classList.remove('open');
        }
    }

    /**
     * @brief Close sidebar
     */
    closeSidebar() {
        const sidebar = document.getElementById('sidebar');
        this.sidebarOpen = false;
        sidebar.classList.remove('open');
    }

    /* -----------------------------------------------------------------
     * Dark Mode
     * ----------------------------------------------------------------- */

    /**
     * @brief Initialise dark-mode state on load
     * @details Reads data-theme (set by inline <script> in HTML head)
     *          and syncs the icon visibility.
     */
    initDarkMode() {
        this.updateDarkModeIcons();
    }

    /**
     * @brief Toggle between light and dark themes
     * @details Persists the choice to localStorage so it survives reloads.
     */
    toggleDarkMode() {
        this.darkMode = !this.darkMode;
        const theme = this.darkMode ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        this.updateDarkModeIcons();
    }

    /**
     * @brief Show / hide the sun & moon SVG icons
     */
    updateDarkModeIcons() {
        const sun = document.querySelector('.icon-sun');
        const moon = document.querySelector('.icon-moon');
        if (sun && moon) {
            sun.style.display = this.darkMode ? 'block' : 'none';
            moon.style.display = this.darkMode ? 'none' : 'block';
        }
    }

    /**
     * @brief Switch between main sections
     * @param {string} section - Section name to switch to
     */
    switchSection(section) {
        // Update navigation
        document.querySelectorAll('.nav-section a').forEach(link => {
            link.classList.remove('active');
            if (link.dataset.section === section) {
                link.classList.add('active');
            }
        });

        // Hide all sections
        document.querySelectorAll('.section').forEach(sec => {
            sec.classList.remove('active');
        });

        // Show selected section
        const targetSection = document.getElementById(section + 'Section');
        if (targetSection) {
            targetSection.classList.add('active');
            this.currentSection = section;
        }
    }

    /**
     * @brief Toggle collapsible card content
     * @param {HTMLElement} header - The header element
     * @param {string} contentId - ID of content element
     */
    toggleCollapsible(header, contentId) {
        const content = document.getElementById(contentId);
        const isOpen = header.classList.contains('open');

        if (isOpen) {
            header.classList.remove('open');
            content.style.display = 'none';
            header.setAttribute('aria-expanded', 'false');
        } else {
            header.classList.add('open');
            content.style.display = 'block';
            header.setAttribute('aria-expanded', 'true');
        }
    }

    /**
     * @brief Check if file type is valid
     * @param {string} filename - Name of the file
     * @returns {boolean} True if valid
     */
    isValidFileType(filename) {
        const validExtensions = ['.pdf', '.txt', '.doc', '.docx'];
        const ext = filename.toLowerCase().substring(filename.lastIndexOf('.'));
        return validExtensions.includes(ext);
    }

    /**
     * @brief Handle file upload
     * @param {File} file - The file to upload
     */
    async handleFileUpload(file) {
        // Show progress
        const progressContainer = document.getElementById('progressContainer');
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');

        progressContainer.style.display = 'block';
        progressFill.style.width = '0%';
        progressText.textContent = 'Uploading...';

        // Simulate upload progress
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += 10;
            if (progress <= 90) {
                progressFill.style.width = progress + '%';
            }
        }, 100);

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/api/extract', {
                method: 'POST',
                body: formData
            });

            clearInterval(progressInterval);
            progressFill.style.width = '100%';
            progressText.textContent = 'Processing complete!';

            const result = await response.json();

            if (result.success) {
                this.displayResults(result);
                this.addToHistory(file.name, true);
                this.showToast('Success', 'Resume processed successfully!', 'success');

                // Switch to results section
                setTimeout(() => {
                    this.switchSection('results');
                    progressContainer.style.display = 'none';
                }, 500);
            } else {
                throw new Error(result.error || 'Processing failed');
            }

        } catch (error) {
            clearInterval(progressInterval);
            progressContainer.style.display = 'none';
            this.addToHistory(file.name, false);
            this.showToast('Error', error.message, 'error');
            console.error('Upload error:', error);
        }
    }

    /**
     * @brief Display extraction results
     * @param {Object} data - The extraction result data
     */
    displayResults(data) {
        // Update confidence badge
        const confidenceValue = document.getElementById('confidenceValue');
        const confidenceBadge = document.getElementById('confidenceBadge');
        const confidence = Math.round((data.confidence_score || 0) * 100);
        confidenceValue.textContent = confidence + '%';

        // Color code confidence
        confidenceBadge.className = 'confidence-badge';
        if (confidence >= 80) {
            confidenceBadge.style.backgroundColor = 'var(--success-color)';
        } else if (confidence >= 60) {
            confidenceBadge.style.backgroundColor = 'var(--warning-color)';
        } else {
            confidenceBadge.style.backgroundColor = 'var(--error-color)';
        }

        // Display skills
        this.displaySkills(data.skills || []);

        // Display education
        this.displayEducation(data.education || []);

        // Display experience
        this.displayExperience(data.experience || []);

        // Display contact info
        this.displayContactInfo(data.contact_info || {});

        // Display raw text
        const rawText = document.getElementById('rawText');
        if (data.raw_text_preview) {
            rawText.textContent = data.raw_text_preview;
        }
    }

    /**
     * @brief Display extracted skills
     * @param {Array} skills - Array of skill strings
     */
    displaySkills(skills) {
        const container = document.getElementById('skillsContainer');
        const badge = document.getElementById('skillsBadge');

        badge.textContent = skills.length + ' found';

        if (skills.length === 0) {
            container.innerHTML = '<p class="empty-state">No skills detected in this resume.</p>';
            return;
        }

        const showConfidence = localStorage.getItem('showConfidence') !== 'false';

        container.innerHTML = skills.map(skill => {
            let confidenceHtml = '';
            if (showConfidence && typeof skill === 'object' && skill.confidence) {
                const confPercent = Math.round(skill.confidence * 100);
                confidenceHtml = `<span class="skill-confidence">${confPercent}%</span>`;
            }
            const skillName = typeof skill === 'string' ? skill : skill.name || skill;
            return `<span class="skill-tag">${skillName}${confidenceHtml}</span>`;
        }).join('');
    }

    /**
     * @brief Update skills display based on settings
     */
    updateSkillsDisplay() {
        // Re-render current skills if available
        const container = document.getElementById('skillsContainer');
        const currentTags = container.querySelectorAll('.skill-tag');
        if (currentTags.length > 0) {
            const skills = Array.from(currentTags).map(tag => {
                const confidenceSpan = tag.querySelector('.skill-confidence');
                return {
                    name: tag.childNodes[0].textContent.trim(),
                    confidence: confidenceSpan ? parseInt(confidenceSpan.textContent) / 100 : 0.8
                };
            });
            this.displaySkills(skills);
        }
    }

    /**
     * @brief Display education information
     * @param {Array} education - Array of education objects
     */
    displayEducation(education) {
        const container = document.getElementById('educationContainer');
        const badge = document.getElementById('educationBadge');

        badge.textContent = education.length + ' found';

        if (education.length === 0) {
            container.innerHTML = '<p class="empty-state">No education information detected.</p>';
            return;
        }

        container.innerHTML = education.map(edu => `
            <div class="education-item">
                <div class="education-title">${this.escapeHtml(edu.degree || 'Unknown Degree')}</div>
                <div class="education-institution">${this.escapeHtml(edu.institution || 'Unknown Institution')}</div>
                ${edu.date ? `<div class="education-date">${this.escapeHtml(edu.date)}</div>` : ''}
            </div>
        `).join('');
    }

    /**
     * @brief Display experience information
     * @param {Array} experience - Array of experience objects
     */
    displayExperience(experience) {
        const container = document.getElementById('experienceContainer');
        const badge = document.getElementById('experienceBadge');

        badge.textContent = experience.length + ' found';

        if (experience.length === 0) {
            container.innerHTML = '<p class="empty-state">No experience information detected.</p>';
            return;
        }

        container.innerHTML = experience.map(exp => `
            <div class="experience-item">
                <div class="experience-title">${this.escapeHtml(exp.title || 'Unknown Position')}</div>
                <div class="experience-company">${this.escapeHtml(exp.company || 'Unknown Company')}</div>
                ${exp.date ? `<div class="experience-date">${this.escapeHtml(exp.date)}</div>` : ''}
            </div>
        `).join('');
    }

    /**
     * @brief Display contact information
     * @param {Object} contact - Contact info object
     */
    displayContactInfo(contact) {
        document.getElementById('emailValue').textContent = contact.email || '-';
        document.getElementById('phoneValue').textContent = contact.phone || '-';
        document.getElementById('linkedinValue').textContent = contact.linkedin || '-';
    }

    /**
     * @brief Add entry to processing history
     * @param {string} filename - Name of processed file
     * @param {boolean} success - Whether processing was successful
     */
    addToHistory(filename, success) {
        const entry = {
            filename: filename,
            date: new Date().toLocaleString(),
            success: success
        };

        this.processingHistory.unshift(entry);
        this.updateHistoryDisplay();
        this.updateStats();
    }

    /**
     * @brief Update history display
     */
    updateHistoryDisplay() {
        const container = document.getElementById('historyList');

        if (this.processingHistory.length === 0) {
            container.innerHTML = '<p class="empty-state">No processing history available.</p>';
            return;
        }

        container.innerHTML = this.processingHistory.map(item => `
            <div class="history-item">
                <div class="history-info">
                    <span class="history-filename">${this.escapeHtml(item.filename)}</span>
                    <span class="history-date">${item.date}</span>
                </div>
                <span class="history-status ${item.success ? 'success' : 'error'}">
                    ${item.success ? 'Success' : 'Failed'}
                </span>
            </div>
        `).join('');
    }

    /**
     * @brief Update statistics display
     */
    updateStats() {
        const processedCount = document.getElementById('processedCount');
        if (processedCount) {
            processedCount.textContent = this.processingHistory.length;
        }
    }

    /**
     * @brief Load skills count from API
     */
    async loadSkillsCount() {
        try {
            const response = await fetch('/api/skills');
            const data = await response.json();

            const skillsCount = document.getElementById('skillsCount');
            if (skillsCount && data.count) {
                skillsCount.textContent = data.count.toLocaleString();
            }
        } catch (error) {
            console.error('Failed to load skills count:', error);
        }
    }

    /**
     * @brief Show toast notification
     * @param {string} title - Toast title
     * @param {string} message - Toast message
     * @param {string} type - Toast type (success, error, warning)
     */
    showToast(title, message, type = 'info') {
        const container = document.getElementById('toastContainer');

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div class="toast-title">${this.escapeHtml(title)}</div>
            <div class="toast-message">${this.escapeHtml(message)}</div>
        `;

        container.appendChild(toast);

        // Remove after 5 seconds
        setTimeout(() => {
            toast.style.animation = 'slideIn 0.3s ease reverse';
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }

    /**
     * @brief Escape HTML special characters
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ResumeExtractorApp();
});

// Health check on load
window.addEventListener('load', async () => {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();

        if (!data.initialized) {
            console.warn('Application not fully initialized');
        }

        console.log('App health:', data);
    } catch (error) {
        console.error('Health check failed:', error);
    }
});
