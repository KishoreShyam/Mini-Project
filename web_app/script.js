// Modern JavaScript with Animations and Interactions

class KeystrokeSecurityApp {
    constructor() {
        this.trainingTexts = [
            "I love to eat pizza and ice cream on sunny days.",
            "My cat likes to sleep on the warm window sill.",
            "The blue car drove slowly down the quiet street.",
            "She reads books every night before going to bed.",
            "We went to the park to play with our friends.",
            "The red apple tastes sweet and fresh from the tree.",
            "He walks his dog every morning at seven o clock.",
            "The children play games in the backyard after school.",
            "I like to drink coffee while watching the sunrise.",
            "The small bird sings beautiful songs in the garden.",
            "We cook dinner together as a family every Sunday.",
            "The green grass grows tall in the summer months.",
            "She writes letters to her grandmother every week.",
            "The warm sun shines bright on the beach today.",
            "I enjoy listening to music while doing my homework."
        ];
        
        this.securityTestTexts = [
            "Hello, this is me typing on my computer.",
            "I am testing the security system right now.",
            "My name is written here for the test.",
            "The weather is nice and sunny today.",
            "I like to type fast on the keyboard.",
            "This is a simple sentence for testing.",
            "The computer knows how I type words.",
            "Security is important for my safety.",
            "I type with my own special style.",
            "This test will check if I am real."
        ];
        
        this.currentSession = 0;
        this.totalSessions = 7;
        this.sessionDuration = 45;
        this.isTraining = false;
        this.startTime = null;
        this.keystrokeData = [];
        this.currentText = '';
        this.alertApiUrl = 'http://localhost:8080/api/alert';
        this.keystrokeApiUrl = 'http://localhost:8080/api/keystroke';
        this.securitySystemActive = false;
        this.failedAttempts = 0;
        this.maxAttempts = 3;
        this.realKeystrokeData = [];
        this.sessionStartTime = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupSliders();
        this.startAnimations();
    }
    
    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });
        
        // Training controls
        document.getElementById('startBtn').addEventListener('click', () => this.startTraining());
        document.getElementById('stopBtn').addEventListener('click', () => this.stopTraining());
        document.getElementById('testBtn').addEventListener('click', () => this.testModel());
        
        // Security controls
        document.getElementById('securityToggle').addEventListener('click', () => this.toggleSecurity());
        document.getElementById('authBtn').addEventListener('click', () => this.testAuthentication());
        
        // Real-time feedback for authentication typing
        document.getElementById('authArea').addEventListener('input', (e) => this.handleAuthTyping(e));
        
        // Typing area events
        const typingArea = document.getElementById('typingArea');
        typingArea.addEventListener('input', (e) => this.handleTyping(e));
        typingArea.addEventListener('keydown', (e) => this.recordKeystroke(e, 'down'));
        typingArea.addEventListener('keyup', (e) => this.recordKeystroke(e, 'up'));
        
        // Authentication area events for real keystroke capture
        const authArea = document.getElementById('authArea');
        authArea.addEventListener('keydown', (e) => this.recordRealKeystroke(e, 'down'));
        authArea.addEventListener('keyup', (e) => this.recordRealKeystroke(e, 'up'));
    }
    
    setupSliders() {
        const sessionsSlider = document.getElementById('sessions');
        const durationSlider = document.getElementById('duration');
        
        sessionsSlider.addEventListener('input', (e) => {
            this.totalSessions = parseInt(e.target.value);
            e.target.nextElementSibling.textContent = e.target.value;
            this.updateSessionDisplay();
        });
        
        durationSlider.addEventListener('input', (e) => {
            this.sessionDuration = parseInt(e.target.value);
            e.target.nextElementSibling.textContent = e.target.value + 's';
        });
    }
    
    startAnimations() {
        // Animate cards on load
        const cards = document.querySelectorAll('.card');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(30px)';
            setTimeout(() => {
                card.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });
        
        // Floating animation for particles
        this.createFloatingParticles();
    }
    
    createFloatingParticles() {
        const particleContainer = document.querySelector('.floating-particles');
        
        for (let i = 0; i < 20; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.cssText = `
                position: absolute;
                width: ${Math.random() * 4 + 2}px;
                height: ${Math.random() * 4 + 2}px;
                background: rgba(255, 255, 255, ${Math.random() * 0.5 + 0.1});
                border-radius: 50%;
                left: ${Math.random() * 100}%;
                top: ${Math.random() * 100}%;
                animation: float ${Math.random() * 10 + 5}s ease-in-out infinite;
                animation-delay: ${Math.random() * 5}s;
            `;
            particleContainer.appendChild(particle);
        }
    }
    
    switchTab(tabName) {
        // Remove active class from all tabs and panels
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));
        
        // Add active class to selected tab and panel
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        document.getElementById(tabName).classList.add('active');
        
        // Animate tab switch
        const activePanel = document.getElementById(tabName);
        activePanel.style.opacity = '0';
        activePanel.style.transform = 'translateX(20px)';
        
        setTimeout(() => {
            activePanel.style.transition = 'all 0.4s ease';
            activePanel.style.opacity = '1';
            activePanel.style.transform = 'translateX(0)';
        }, 50);
        
        this.showNotification(`Switched to ${tabName.charAt(0).toUpperCase() + tabName.slice(1)} tab`, 'success');
    }
    
    startTraining() {
        this.isTraining = true;
        this.currentSession = 0;
        this.keystrokeData = [];
        
        // Update UI
        document.getElementById('startBtn').disabled = true;
        document.getElementById('stopBtn').disabled = false;
        document.getElementById('typingArea').disabled = false;
        
        // Add visual feedback
        document.querySelector('.text-display').classList.add('active');
        
        this.showNotification('Training started! Type the displayed text.', 'success');
        this.startNextSession();
    }
    
    async startNextSession() {
        if (!this.isTraining || this.currentSession >= this.totalSessions) {
            this.completeTraining();
            return;
        }
        
        this.currentText = this.getRandomText();
        this.startTime = Date.now();
        
        // Update display
        document.getElementById('textDisplay').textContent = this.currentText;
        document.getElementById('typingArea').value = '';
        document.getElementById('typingArea').focus();
        
        this.updateSessionDisplay();
        this.updateProgress(0);
        
        // Start session timer
        this.sessionTimer = setInterval(() => {
            const elapsed = (Date.now() - this.startTime) / 1000;
            const remaining = Math.max(0, this.sessionDuration - elapsed);
            const progress = (elapsed / this.sessionDuration) * 100;
            
            this.updateProgress(Math.min(progress, 100));
            document.getElementById('timeRemaining').textContent = 
                remaining > 0 ? `${Math.ceil(remaining)}s remaining` : 'Time up!';
            
            if (remaining <= 0) {
                this.endCurrentSession();
            }
        }, 100);
        
        // Animate session start
        this.animateSessionStart();
    }
    
    animateSessionStart() {
        const textDisplay = document.getElementById('textDisplay');
        textDisplay.style.transform = 'scale(0.95)';
        textDisplay.style.opacity = '0.7';
        
        setTimeout(() => {
            textDisplay.style.transition = 'all 0.3s ease';
            textDisplay.style.transform = 'scale(1)';
            textDisplay.style.opacity = '1';
        }, 100);
    }
    
    endCurrentSession() {
        clearInterval(this.sessionTimer);
        
        // Show session complete animation
        this.showNotification(`Session ${this.currentSession} completed!`, 'success');
        
        // Brief pause before next session
        setTimeout(() => {
            if (this.isTraining) {
                this.startNextSession();
            }
        }, 2000);
    }
    
    stopTraining() {
        this.isTraining = false;
        clearInterval(this.sessionTimer);
        
        // Reset UI
        document.getElementById('startBtn').disabled = false;
        document.getElementById('stopBtn').disabled = true;
        document.getElementById('typingArea').disabled = true;
        document.querySelector('.text-display').classList.remove('active');
        
        this.updateProgress(0);
        document.getElementById('progressText').textContent = 'Training stopped';
        document.getElementById('timeRemaining').textContent = '';
        
        this.showNotification('Training stopped by user', 'warning');
    }
    
    async saveTrainingSession() {
        if (this.keystrokeData.length === 0) return;
        
        const sessionData = {
            text: this.currentText,
            keystrokes: this.keystrokeData,
            typing_speed: this.calculateTypingSpeed(),
            accuracy: this.calculateAccuracy(),
            duration: (Date.now() - this.startTime) / 1000
        };
        
        const result = await this.callKeystrokeAPI('/save', sessionData);
        if (result.success) {
            this.showNotification(`Session ${result.session_id} saved! Total: ${result.total_sessions}`, 'success');
        }
        
        this.keystrokeData = []; // Reset for next session
    }
    
    calculateTypingSpeed() {
        if (!this.currentText || !this.startTime) return 0;
        const timeMinutes = (Date.now() - this.startTime) / 60000;
        const wordsTyped = this.currentText.split(' ').length;
        return Math.round(wordsTyped / timeMinutes);
    }
    
    calculateAccuracy() {
        const typedText = document.getElementById('typingArea').value;
        if (!typedText || !this.currentText) return 0;
        
        let correct = 0;
        const minLength = Math.min(typedText.length, this.currentText.length);
        
        for (let i = 0; i < minLength; i++) {
            if (typedText[i] === this.currentText[i]) correct++;
        }
        
        return correct / this.currentText.length;
    }

    async completeTraining() {
        this.isTraining = false;
        clearInterval(this.sessionTimer);
        
        // Train the model if we have enough sessions
        this.showNotification('Training model with your typing patterns...', 'info');
        const trainResult = await this.callKeystrokeAPI('/train', {});
        
        if (trainResult.success) {
            this.showNotification(`🎉 Training complete! Model accuracy: ${Math.round(trainResult.accuracy * 100)}%`, 'success');
        } else {
            this.showNotification(trainResult.message || 'Model training failed', 'warning');
        }
        
        // Reset UI
        document.getElementById('startBtn').disabled = false;
        document.getElementById('stopBtn').disabled = true;
        document.getElementById('typingArea').disabled = true;
        document.querySelector('.text-display').classList.remove('active');
        
        // Show completion animation
        this.animateTrainingComplete();
        
        // Simulate model training
        this.simulateModelTraining();
    }
    
    animateTrainingComplete() {
        const progressCard = document.querySelector('.progress-card');
        progressCard.style.background = 'linear-gradient(135deg, #10b981, #059669)';
        progressCard.style.transform = 'scale(1.02)';
        
        setTimeout(() => {
            progressCard.style.transition = 'all 0.5s ease';
            progressCard.style.transform = 'scale(1)';
        }, 200);
        
        this.showNotification('🎉 Training completed successfully!', 'success');
    }
    
    simulateModelTraining() {
        document.getElementById('progressText').textContent = 'Training AI model...';
        let progress = 0;
        
        const modelTraining = setInterval(() => {
            progress += Math.random() * 10;
            if (progress >= 100) {
                progress = 100;
                clearInterval(modelTraining);
                document.getElementById('progressText').textContent = 
                    `Model trained with ${this.keystrokeData.length} keystroke samples`;
                this.showNotification('AI model training completed!', 'success');
            }
            this.updateProgress(progress);
        }, 200);
    }
    
    handleTyping(e) {
        if (!this.isTraining) return;
        
        const typed = e.target.value;
        const target = this.currentText;
        
        // Calculate accuracy
        let correct = 0;
        for (let i = 0; i < Math.min(typed.length, target.length); i++) {
            if (typed[i] === target[i]) correct++;
        }
        
        const accuracy = typed.length > 0 ? (correct / typed.length * 100).toFixed(1) : 0;
        document.getElementById('accuracy').textContent = accuracy + '%';
        
        // Calculate WPM
        const timeElapsed = (Date.now() - this.startTime) / 1000 / 60; // minutes
        const wordsTyped = typed.split(' ').length;
        const wpm = timeElapsed > 0 ? Math.round(wordsTyped / timeElapsed) : 0;
        document.getElementById('wpm').textContent = wpm;
        
        // Visual feedback for accuracy
        const typingArea = e.target;
        if (accuracy >= 90) {
            typingArea.style.borderColor = '#10b981';
        } else if (accuracy >= 70) {
            typingArea.style.borderColor = '#f59e0b';
        } else {
            typingArea.style.borderColor = '#ef4444';
        }
    }
    
    recordKeystroke(event, type) {
        if (!this.isTraining) return;
        
        const keystroke = {
            key: event.key,
            code: event.code,
            type: type,
            timestamp: Date.now() - this.startTime,
            ctrlKey: event.ctrlKey,
            shiftKey: event.shiftKey,
            altKey: event.altKey
        };
        
        this.keystrokeData.push(keystroke);
    }
    
    recordRealKeystroke(event, type) {
        // Record real keystrokes for authentication
        if (!this.sessionStartTime) {
            this.sessionStartTime = Date.now();
        }
        
        const keystroke = {
            key: event.key,
            code: event.code,
            type: type,
            timestamp: Date.now() - this.sessionStartTime,
            ctrlKey: event.ctrlKey,
            shiftKey: event.shiftKey,
            altKey: event.altKey
        };
        
        this.realKeystrokeData.push(keystroke);
    }
    
    updateProgress(percentage) {
        document.getElementById('progressFill').style.width = percentage + '%';
    }
    
    updateSessionDisplay() {
        document.getElementById('sessionCount').textContent = 
            `${this.currentSession}/${this.totalSessions}`;
    }
    
    getRandomText() {
        return this.trainingTexts[Math.floor(Math.random() * this.trainingTexts.length)];
    }
    
    getRandomSecurityText() {
        return this.securityTestTexts[Math.floor(Math.random() * this.securityTestTexts.length)];
    }
    
    testModel() {
        this.switchTab('security');
        this.showNotification('Switched to Security tab for model testing', 'success');
    }
    
    startAuthenticationTest() {
        const authArea = document.getElementById('authArea');
        const authBtn = document.getElementById('authBtn');
        const authTextDisplay = document.getElementById('authTextDisplay');
        
        // Get random test text
        const testText = this.getRandomSecurityText();
        
        // Show the text to type in the display area
        authTextDisplay.textContent = testText;
        authTextDisplay.classList.add('active');
        
        // Clear the typing area and focus
        authArea.value = '';
        authArea.placeholder = 'Type the text shown above here...';
        authArea.focus();
        
        // Update button - don't pass the old testText, let the function get it from display
        authBtn.innerHTML = '<i class="fas fa-keyboard"></i><span>Complete Test</span>';
        authBtn.onclick = () => this.completeAuthenticationTest();
        
        this.showNotification('Type the text shown in the yellow box above', 'info');
    }
    
    completeAuthenticationTest() {
        const authArea = document.getElementById('authArea');
        const authBtn = document.getElementById('authBtn');
        const authTextDisplay = document.getElementById('authTextDisplay');
        const typedText = authArea.value.trim();
        
        // Always get the expected text from the display
        const textToCompare = authTextDisplay.textContent.trim();
        
        if (!textToCompare) {
            this.showNotification('No text to compare against. Please start a new test.', 'error');
            return;
        }
        
        // Debug: Show what we're comparing
        console.log('Expected text:', `"${textToCompare}" (${textToCompare.length} chars)`);
        console.log('Typed text:', `"${typedText}" (${typedText.length} chars)`);
        
        // Check if user has typed something substantial (at least 60% of expected length)
        const minLength = Math.floor(textToCompare.length * 0.6);
        if (typedText.length < minLength) {
            this.showNotification(`Please type more of the text (${typedText.length}/${textToCompare.length} characters needed)`, 'warning');
            return;
        }
        
        // If user has typed at least 90% of the text, proceed with authentication
        if (typedText.length >= textToCompare.length * 0.9) {
            // Proceed with authentication regardless of exact match
        }
        
        // Simulate authentication
        authArea.disabled = true;
        authBtn.disabled = true;
        
        // Show loading animation
        authBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Analyzing...</span>';
        
        setTimeout(async () => {
            // Use real ML authentication if available
            const authData = {
                text: textToCompare,
                keystrokes: this.realKeystrokeData,
                typing_speed: this.calculateAuthTypingSpeed(),
                accuracy: this.calculateAuthAccuracy(typedText, textToCompare),
                duration: this.sessionStartTime ? (Date.now() - this.sessionStartTime) / 1000 : 0
            };
            
            const authResult = await this.callKeystrokeAPI('/authenticate', authData);
            
            let isAuthentic, similarity;
            
            if (authResult.success && authResult.confidence !== undefined) {
                // Use ML authentication result
                isAuthentic = authResult.is_authentic;
                similarity = authResult.confidence;
                console.log('🤖 ML Authentication:', isAuthentic ? 'AUTHENTIC' : 'SUSPICIOUS', `(${Math.round(similarity * 100)}%)`);
            } else {
                // Fallback to text similarity
                similarity = this.calculateSimilarity(typedText.toLowerCase(), textToCompare.toLowerCase());
                isAuthentic = similarity > 0.6;
                console.log('📝 Text-based Authentication:', isAuthentic ? 'PASS' : 'FAIL', `(${Math.round(similarity * 100)}%)`);
            }
            
            if (isAuthentic) {
                authArea.style.borderColor = '#10b981';
                authArea.style.background = 'rgba(16, 185, 129, 0.1)';
                this.showNotification(`✅ Authentication Successful! (${Math.round(similarity * 100)}% match)`, 'success');
                this.failedAttempts = 0; // Reset failed attempts on success
            } else {
                authArea.style.borderColor = '#ef4444';
                authArea.style.background = 'rgba(239, 68, 68, 0.1)';
                this.failedAttempts++;
                
                if (this.securitySystemActive && this.failedAttempts >= this.maxAttempts) {
                    this.showNotification(`🚨 SECURITY BREACH! ${this.failedAttempts} failed attempts!`, 'error');
                    // Trigger security breach alert
                    setTimeout(() => this.triggerSecurityBreach(), 1000);
                } else {
                    this.showNotification(`❌ Authentication Failed! (${Math.round(similarity * 100)}% match) - Attempt ${this.failedAttempts}/${this.maxAttempts}`, 'error');
                }
            }
            
            // Reset after 4 seconds
            setTimeout(() => {
                const authTextDisplay = document.getElementById('authTextDisplay');
                
                authArea.disabled = false;
                authBtn.disabled = false;
                authBtn.innerHTML = '<i class="fas fa-key"></i><span>Test Authentication</span>';
                authBtn.onclick = () => this.startAuthenticationTest();
                authArea.style.borderColor = '';
                authArea.style.background = '';
                authArea.value = '';
                authArea.placeholder = 'Type the text shown above here...';
                
                // Reset text display
                authTextDisplay.textContent = 'Click "Test Authentication" to get a sentence to type';
                authTextDisplay.classList.remove('active');
                
                // Reset keystroke data
                this.realKeystrokeData = [];
                this.sessionStartTime = null;
            }, 4000);
            
        }, 2000);
    }
    
    calculateSimilarity(str1, str2) {
        const longer = str1.length > str2.length ? str1 : str2;
        const shorter = str1.length > str2.length ? str2 : str1;
        
        if (longer.length === 0) return 1.0;
        
        const editDistance = this.levenshteinDistance(longer, shorter);
        return (longer.length - editDistance) / longer.length;
    }
    
    levenshteinDistance(str1, str2) {
        const matrix = [];
        
        for (let i = 0; i <= str2.length; i++) {
            matrix[i] = [i];
        }
        
        for (let j = 0; j <= str1.length; j++) {
            matrix[0][j] = j;
        }
        
        for (let i = 1; i <= str2.length; i++) {
            for (let j = 1; j <= str1.length; j++) {
                if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
                    matrix[i][j] = matrix[i - 1][j - 1];
                } else {
                    matrix[i][j] = Math.min(
                        matrix[i - 1][j - 1] + 1,
                        matrix[i][j - 1] + 1,
                        matrix[i - 1][j] + 1
                    );
                }
            }
        }
        
        return matrix[str2.length][str1.length];
    }
    
    calculateAuthTypingSpeed() {
        if (!this.sessionStartTime) return 0;
        const timeMinutes = (Date.now() - this.sessionStartTime) / 60000;
        const authArea = document.getElementById('authArea');
        const wordsTyped = authArea.value.split(' ').length;
        return Math.round(wordsTyped / timeMinutes);
    }
    
    calculateAuthAccuracy(typedText, expectedText) {
        if (!typedText || !expectedText) return 0;
        
        let correct = 0;
        const minLength = Math.min(typedText.length, expectedText.length);
        
        for (let i = 0; i < minLength; i++) {
            if (typedText[i] === expectedText[i]) correct++;
        }
        
        return correct / expectedText.length;
    }
    
    handleAuthTyping(e) {
        const authArea = e.target;
        const authTextDisplay = document.getElementById('authTextDisplay');
        const expectedText = authTextDisplay.textContent.trim();
        
        // Only provide feedback if we're in an active test
        if (!authTextDisplay.classList.contains('active') || !expectedText) return;
        
        const typedText = authArea.value;
        const progress = (typedText.length / expectedText.length * 100).toFixed(0);
        
        // Update placeholder with progress
        authArea.placeholder = `Progress: ${progress}% (${typedText.length}/${expectedText.length} characters)`;
        
        // Visual feedback based on accuracy
        let correct = 0;
        for (let i = 0; i < Math.min(typedText.length, expectedText.length); i++) {
            if (typedText[i].toLowerCase() === expectedText[i].toLowerCase()) {
                correct++;
            }
        }
        
        const accuracy = typedText.length > 0 ? (correct / typedText.length * 100) : 100;
        
        // Color feedback (more lenient thresholds)
        if (accuracy >= 85) {
            authArea.style.borderColor = '#10b981'; // Green
        } else if (accuracy >= 65) {
            authArea.style.borderColor = '#f59e0b'; // Yellow
        } else {
            authArea.style.borderColor = '#ef4444'; // Red
        }
        
        // Auto-complete when user has typed enough (more lenient)
        if (typedText.length >= expectedText.length * 0.8 && accuracy >= 70) {
            // Change button text to indicate ready
            const authBtn = document.getElementById('authBtn');
            authBtn.innerHTML = '<i class="fas fa-check"></i><span>Ready - Complete Test</span>';
            authBtn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
        } else {
            // Reset button if conditions not met
            const authBtn = document.getElementById('authBtn');
            if (authBtn.innerHTML.includes('Ready')) {
                authBtn.innerHTML = '<i class="fas fa-keyboard"></i><span>Complete Test</span>';
                authBtn.style.background = '';
            }
        }
    }
    
    testAuthentication() {
        this.startAuthenticationTest();
    }
    
    // Mobile Alert System Integration
    async callAlertAPI(endpoint, data = {}) {
        try {
            const response = await fetch(`${this.alertApiUrl}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            console.error('Alert API error:', error);
            return { success: false, error: error.message };
        }
    }
    
    async callKeystrokeAPI(endpoint, data = {}) {
        try {
            const response = await fetch(`${this.keystrokeApiUrl}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            console.error('Keystroke API error:', error);
            return { success: false, error: error.message };
        }
    }
    
    async testAlertSystem(type = 'all') {
        this.showNotification('Testing alert system...', 'info');
        
        const result = await this.callAlertAPI('/test', { type });
        
        if (result.success) {
            this.showNotification(`✅ ${result.message}`, 'success');
        } else {
            this.showNotification(`❌ Alert test failed: ${result.error}`, 'error');
        }
        
        return result;
    }
    
    async triggerSecurityBreach() {
        this.showNotification('🚨 SECURITY BREACH DETECTED!', 'error');
        
        const breachDetails = {
            timestamp: new Date().toISOString(),
            failedAttempts: this.failedAttempts,
            maxAttempts: this.maxAttempts,
            userAgent: navigator.userAgent,
            location: window.location.href
        };
        
        const result = await this.callAlertAPI('/breach', { details: breachDetails });
        
        if (result.success) {
            this.showNotification(`📱 Emergency alerts sent to ${result.mobile_number}!`, 'success');
        } else {
            this.showNotification(`❌ Failed to send alerts: ${result.error}`, 'error');
        }
        
        return result;
    }
    
    toggleSecurity() {
        const btn = document.getElementById('securityToggle');
        const statusCircle = document.getElementById('statusCircle');
        const statusTitle = document.getElementById('statusTitle');
        const statusDesc = document.getElementById('statusDesc');
        
        if (statusCircle.classList.contains('stopped')) {
            // Start security system
            this.securitySystemActive = true;
            this.failedAttempts = 0; // Reset failed attempts
            
            statusCircle.classList.remove('stopped');
            statusCircle.classList.add('running');
            statusTitle.textContent = 'System Running';
            statusDesc.textContent = `Security monitoring active - Max ${this.maxAttempts} failed attempts allowed`;
            btn.innerHTML = '<i class="fas fa-power-off"></i><span>Stop Security System</span>';
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-danger');
            
            this.showNotification(`🔒 Security system activated! Mobile alerts to +918015339335`, 'success');
            
            // Update status indicator in header
            document.querySelector('.status-indicator span').textContent = 'System Active';
            
        } else {
            // Stop security system
            this.securitySystemActive = false;
            this.failedAttempts = 0; // Reset failed attempts
            
            statusCircle.classList.remove('running');
            statusCircle.classList.add('stopped');
            statusTitle.textContent = 'System Stopped';
            statusDesc.textContent = 'Security monitoring is inactive';
            btn.innerHTML = '<i class="fas fa-power-off"></i><span>Start Security System</span>';
            btn.classList.remove('btn-danger');
            btn.classList.add('btn-primary');
            
            this.showNotification('Security system deactivated', 'warning');
            
            // Update status indicator in header
            document.querySelector('.status-indicator span').textContent = 'System Ready';
        }
    }
    
    showNotification(message, type = 'success') {
        const notification = document.getElementById('notification');
        const icon = notification.querySelector('.notification-icon');
        const text = notification.querySelector('.notification-text');
        
        // Set icon based on type
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        icon.className = `notification-icon ${icons[type]}`;
        text.textContent = message;
        notification.className = `notification ${type}`;
        
        // Show notification
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Hide after 4 seconds
        setTimeout(() => {
            notification.classList.remove('show');
        }, 4000);
    }
}

// Initialize app when DOM is loaded
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new KeystrokeSecurityApp();
    window.app = app; // Make globally accessible for onclick handlers
});

// Add some extra visual effects
document.addEventListener('mousemove', (e) => {
    const cursor = document.createElement('div');
    cursor.style.cssText = `
        position: fixed;
        width: 10px;
        height: 10px;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.3) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
        z-index: 9999;
        left: ${e.clientX - 5}px;
        top: ${e.clientY - 5}px;
        animation: cursorFade 0.5s ease-out forwards;
    `;
    
    document.body.appendChild(cursor);
    
    setTimeout(() => cursor.remove(), 500);
});

// Add cursor fade animation
const style = document.createElement('style');
style.textContent = `
    @keyframes cursorFade {
        0% { opacity: 1; transform: scale(1); }
        100% { opacity: 0; transform: scale(0.5); }
    }
`;
document.head.appendChild(style);
