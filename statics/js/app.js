const ShidaApp = {
    currentUser: null,
    profiles: [],
    currentProfileIndex: 0,
    
    async init() {
        this.createParticles();
        await this.checkAuth();
    },
    
    createParticles() {
        const container = document.querySelector('.particles');
        if (!container) return;
        
        for (let i = 0; i < 20; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 10 + 's';
            particle.style.animationDuration = (10 + Math.random() * 10) + 's';
            container.appendChild(particle);
        }
    },
    
    async checkAuth() {
        try {
            const response = await fetch('/api/auth/me');
            if (response.ok) {
                this.currentUser = await response.json();
            }
        } catch (error) {
            console.log('Not authenticated');
        }
        window.dispatchEvent(new CustomEvent('ShidaReady'));
    },
    
    async login(email, password) {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        if (data.success) {
            window.location.href = '/home';
        } else {
            this.showError(data.error || 'Login failed');
        }
    },
    
    async register(name, email, password, age) {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password, age: parseInt(age) })
        });
        
        const data = await response.json();
        if (data.success) {
            window.location.href = '/home';
        } else {
            this.showError(data.error || 'Registration failed');
        }
    },
    
    async logout() {
        await fetch('/api/auth/logout', { method: 'POST' });
        window.location.href = '/';
    },
    
    showError(message) {
        alert(message);
    }
};

const Dashboard = {
    async loadStats() {
        try {
            const response = await fetch('/api/dashboard/stats');
            const stats = await response.json();
            this.renderStats(stats);
        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    },
    
    renderStats(stats) {
        const viewsEl = document.getElementById('viewsCount');
        if (viewsEl) {
            this.animateNumber(viewsEl, 0, stats.views_total);
        }
        
        const changeEl = document.getElementById('viewsChange');
        if (changeEl) {
            changeEl.textContent = `↗ +${stats.views_change_percent}%`;
        }
        
        const chartBars = document.querySelectorAll('.chart-bar');
        const maxView = Math.max(...stats.views_weekly, 1);
        chartBars.forEach((bar, index) => {
            const height = (stats.views_weekly[index] / maxView) * 100;
            setTimeout(() => {
                bar.style.height = Math.max(height, 10) + '%';
            }, index * 100);
        });
        
        const tokensEl = document.getElementById('tokensCount');
        if (tokensEl) {
            this.animateNumber(tokensEl, 0, stats.tokens);
        }
        
        const negoEl = document.getElementById('negoCount');
        if (negoEl) {
            this.animateNumber(negoEl, 0, stats.negotiations_count);
        }
        
        const vipTypeEl = document.getElementById('vipType');
        if (vipTypeEl && stats.is_vip) {
            vipTypeEl.textContent = `VIP ${stats.vip_type}`;
        }
    },
    
    animateNumber(element, start, end) {
        const duration = 1000;
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const current = Math.round(start + (end - start) * easeOut);
            element.textContent = current;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }
};

const Discovery = {
    profiles: [],
    currentIndex: 0,
    startX: 0,
    currentX: 0,
    isDragging: false,
    
    async init() {
        await this.loadProfiles();
        this.setupSwipeHandlers();
    },
    
    async loadProfiles() {
        try {
            const response = await fetch('/api/discovery');
            this.profiles = await response.json();
            this.renderCurrentCard();
        } catch (error) {
            console.error('Failed to load profiles:', error);
        }
    },
    
    renderCurrentCard() {
        const stack = document.getElementById('cardStack');
        if (!stack) return;
        
        stack.innerHTML = '';
        
        if (this.currentIndex >= this.profiles.length) {
            stack.innerHTML = `
                <div class="stat-card" style="text-align: center; padding: 40px;">
                    <div style="font-size: 3rem; margin-bottom: 20px;">💫</div>
                    <h3>Plus de profils disponibles</h3>
                    <p style="color: var(--text-gray); margin-top: 10px;">Revenez plus tard pour découvrir de nouveaux profils</p>
                </div>
            `;
            return;
        }
        
        const profile = this.profiles[this.currentIndex];
        
        const card = document.createElement('div');
        card.className = 'profile-card';
        card.id = 'currentCard';
        card.innerHTML = `
            <img src="${profile.photo_url || 'https://via.placeholder.com/400x450'}" alt="${profile.name}" class="profile-image">
            <div class="profile-info">
                <span class="objective-badge">💎 ${profile.objective || 'Mariage & Sérieux'}</span>
                <div class="profile-name">
                    ${profile.name}, ${profile.age}
                    <span class="verified-badge">⊙</span>
                </div>
            </div>
            <div class="swipe-indicator left">✕</div>
            <div class="swipe-indicator right">♥</div>
            <div class="swipe-overlay like">
                <svg viewBox="0 0 24 24"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>
            </div>
            <div class="swipe-overlay dislike">
                <svg viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            </div>
        `;
        
        stack.appendChild(card);
        this.setupCardSwipe(card);
    },
    
    setupSwipeHandlers() {
        const dislikeBtn = document.getElementById('dislikeBtn');
        const likeBtn = document.getElementById('likeBtn');
        
        if (dislikeBtn) {
            dislikeBtn.addEventListener('click', () => {
                this.showButtonFeedback('left');
                setTimeout(() => this.swipe('left'), 200);
            });
        }
        
        if (likeBtn) {
            likeBtn.addEventListener('click', () => {
                this.showButtonFeedback('right');
                setTimeout(() => this.swipe('right'), 200);
            });
        }
    },
    
    showButtonFeedback(direction) {
        const card = document.getElementById('currentCard');
        if (!card) return;
        
        const overlay = direction === 'right' 
            ? card.querySelector('.swipe-overlay.like')
            : card.querySelector('.swipe-overlay.dislike');
        
        if (overlay) {
            overlay.style.opacity = '0.8';
            overlay.style.transition = 'opacity 0.2s ease';
        }
    },
    
    setupCardSwipe(card) {
        card.addEventListener('mousedown', (e) => this.startDrag(e));
        card.addEventListener('touchstart', (e) => this.startDrag(e.touches[0]));
        
        document.addEventListener('mousemove', (e) => this.drag(e));
        document.addEventListener('touchmove', (e) => this.drag(e.touches[0]));
        
        document.addEventListener('mouseup', () => this.endDrag());
        document.addEventListener('touchend', () => this.endDrag());
    },
    
    startDrag(e) {
        this.isDragging = true;
        this.startX = e.clientX;
    },
    
    drag(e) {
        if (!this.isDragging) return;
        
        const card = document.getElementById('currentCard');
        if (!card) return;
        
        this.currentX = e.clientX - this.startX;
        const rotation = this.currentX * 0.1;
        
        card.style.transform = `translateX(${this.currentX}px) rotate(${rotation}deg)`;
        
        const leftIndicator = card.querySelector('.swipe-indicator.left');
        const rightIndicator = card.querySelector('.swipe-indicator.right');
        const likeOverlay = card.querySelector('.swipe-overlay.like');
        const dislikeOverlay = card.querySelector('.swipe-overlay.dislike');
        
        if (this.currentX < -50) {
            const opacity = Math.min(1, Math.abs(this.currentX) / 150);
            leftIndicator.style.opacity = opacity;
            rightIndicator.style.opacity = 0;
            if (dislikeOverlay) dislikeOverlay.style.opacity = opacity * 0.8;
            if (likeOverlay) likeOverlay.style.opacity = 0;
        } else if (this.currentX > 50) {
            const opacity = Math.min(1, this.currentX / 150);
            rightIndicator.style.opacity = opacity;
            leftIndicator.style.opacity = 0;
            if (likeOverlay) likeOverlay.style.opacity = opacity * 0.8;
            if (dislikeOverlay) dislikeOverlay.style.opacity = 0;
        } else {
            leftIndicator.style.opacity = 0;
            rightIndicator.style.opacity = 0;
            if (likeOverlay) likeOverlay.style.opacity = 0;
            if (dislikeOverlay) dislikeOverlay.style.opacity = 0;
        }
    },
    
    endDrag() {
        if (!this.isDragging) return;
        this.isDragging = false;
        
        const card = document.getElementById('currentCard');
        if (!card) return;
        
        if (this.currentX < -100) {
            this.swipe('left');
        } else if (this.currentX > 100) {
            this.swipe('right');
        } else {
            card.style.transform = '';
            const indicators = card.querySelectorAll('.swipe-indicator');
            indicators.forEach(ind => ind.style.opacity = 0);
        }
        
        this.currentX = 0;
    },
    
    async swipe(direction) {
        const card = document.getElementById('currentCard');
        if (!card || this.currentIndex >= this.profiles.length) return;
        
        if (!ShidaApp.currentUser) {
            window.location.href = '/login';
            return;
        }
        
        const profile = this.profiles[this.currentIndex];
        
        card.classList.add(direction === 'left' ? 'swiping-left' : 'swiping-right');
        
        try {
            const response = await fetch('/api/discovery/swipe', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    profile_id: profile.id,
                    direction: direction
                })
            });
            
            const result = await response.json();
            
            if (result.match) {
                setTimeout(() => this.showMatchPopup(result.match_data), 500);
            }
        } catch (error) {
            console.error('Swipe error:', error);
        }
        
        setTimeout(() => {
            this.currentIndex++;
            this.renderCurrentCard();
        }, 500);
    },
    
    showMatchPopup(matchData) {
        const overlay = document.getElementById('matchOverlay');
        if (!overlay) return;
        
        this.createConfetti();
        
        const otherUser = matchData.user2;
        
        const popup = overlay.querySelector('.match-popup');
        const avatarContainer = popup.querySelector('.match-profiles');
        
        avatarContainer.innerHTML = `
            <img src="${ShidaApp.currentUser?.profile?.photo_url || 'https://via.placeholder.com/80'}" class="match-avatar" alt="You">
            <span class="match-connector">—</span>
            <img src="${otherUser?.photo_url || 'https://via.placeholder.com/80'}" class="match-avatar" alt="${otherUser?.name}">
        `;
        
        overlay.classList.add('active');
    },
    
    hideMatchPopup() {
        const overlay = document.getElementById('matchOverlay');
        if (overlay) {
            overlay.classList.remove('active');
        }
    },
    
    createConfetti() {
        const colors = ['#ff1493', '#ffd700', '#00ff88', '#ff4444', '#4444ff'];
        
        for (let i = 0; i < 50; i++) {
            const confetti = document.createElement('div');
            confetti.className = 'confetti';
            confetti.style.left = Math.random() * 100 + '%';
            confetti.style.top = '-10px';
            confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
            confetti.style.animationDelay = Math.random() * 0.5 + 's';
            document.body.appendChild(confetti);
            
            setTimeout(() => confetti.remove(), 3000);
        }
    },
    
    async useTokenAndChat(matchId) {
        try {
            await fetch('/api/tokens/use', { method: 'POST' });
            window.location.href = `/chat/${matchId}`;
        } catch (error) {
            console.error('Error:', error);
        }
    }
};

const Negotiations = {
    async loadMatches() {
        try {
            const response = await fetch('/api/matches');
            const matches = await response.json();
            this.renderMatches(matches);
        } catch (error) {
            console.error('Failed to load matches:', error);
        }
    },
    
    renderMatches(matches) {
        const list = document.getElementById('conversationList');
        if (!list) return;
        
        if (matches.length === 0) {
            list.innerHTML = `
                <div class="stat-card" style="text-align: center;">
                    <div style="font-size: 3rem; margin-bottom: 15px;">💬</div>
                    <p style="color: var(--text-gray);">Aucune négociation en cours</p>
                    <a href="/discovery" class="cta-button" style="margin-top: 20px;">Explorer le marché</a>
                </div>
            `;
            return;
        }
        
        const subtitle = document.getElementById('matchesCount');
        if (subtitle) {
            subtitle.textContent = `${matches.length} Affaires en cours`;
        }
        
        list.innerHTML = matches.map(match => {
            const other = match.other_user;
            const isShidaTeam = other?.name === 'Équipe Shida';
            
            return `
                <a href="/chat/${match.id}" class="conversation-item">
                    <img src="${other?.photo_url || 'https://via.placeholder.com/55'}" alt="${other?.name}" class="conversation-avatar">
                    <div class="conversation-info">
                        <div class="conversation-name">
                            ${other?.name || 'Unknown'}, ${other?.age || ''}
                            ${match.unread_count > 0 ? `<span class="unread-badge">${match.unread_count}</span>` : ''}
                        </div>
                        <div class="conversation-preview ${isShidaTeam ? 'shida' : ''}">
                            ${match.last_message?.content || 'Démarrer la conversation...'}
                        </div>
                    </div>
                </a>
            `;
        }).join('');
    }
};

const Chat = {
    matchId: null,
    messages: [],
    
    init(matchId) {
        this.matchId = matchId;
        this.loadMessages();
        this.setupMessageInput();
    },
    
    async loadMessages() {
        try {
            const response = await fetch(`/api/matches/${this.matchId}/messages`);
            this.messages = await response.json();
            this.renderMessages();
        } catch (error) {
            console.error('Failed to load messages:', error);
        }
    },
    
    renderMessages() {
        const container = document.getElementById('chatMessages');
        if (!container) return;
        
        container.innerHTML = this.messages.map(msg => {
            const isSent = msg.sender_id === ShidaApp.currentUser?.id;
            const time = new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            
            return `
                <div class="message ${isSent ? 'sent' : 'received'}">
                    <div class="message-bubble">${msg.content}</div>
                    <div class="message-time">${time}</div>
                </div>
            `;
        }).join('');
        
        container.scrollTop = container.scrollHeight;
    },
    
    setupMessageInput() {
        const input = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        
        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendMessage());
        }
        
        if (input) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.sendMessage();
            });
        }
    },
    
    async sendMessage() {
        const input = document.getElementById('messageInput');
        if (!input || !input.value.trim()) return;
        
        const content = input.value.trim();
        input.value = '';
        
        try {
            const response = await fetch(`/api/matches/${this.matchId}/messages`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content })
            });
            
            const newMessage = await response.json();
            this.messages.push(newMessage);
            this.renderMessages();
        } catch (error) {
            console.error('Failed to send message:', error);
        }
    }
};

const Profile = {
    async loadProfile() {
        try {
            const response = await fetch('/api/profile');
            const profile = await response.json();
            this.renderProfile(profile);
        } catch (error) {
            console.error('Failed to load profile:', error);
        }
    },
    
    renderProfile(profile) {
        const avatarEl = document.getElementById('profileAvatar');
        if (avatarEl) {
            avatarEl.src = profile.photo_url || 'https://via.placeholder.com/150';
        }
        
        const nameEl = document.getElementById('profileName');
        if (nameEl) {
            nameEl.innerHTML = `${profile.name || 'User'}, ${profile.age || ''} <span class="verified-badge">⊙</span>`;
        }
        
        const religionEl = document.getElementById('profileReligion');
        if (religionEl) {
            religionEl.textContent = profile.religion || 'Non spécifié';
        }
        
        const tribeEl = document.getElementById('profileTribe');
        if (tribeEl) {
            tribeEl.textContent = profile.tribe || 'Non spécifié';
        }
        
        const professionEl = document.getElementById('profileProfession');
        if (professionEl) {
            professionEl.textContent = profile.profession || 'Non spécifié';
        }
    },
    
    async toggleGhostMode() {
        try {
            const response = await fetch('/api/profile/ghost-mode', { method: 'POST' });
            const result = await response.json();
            return result.ghost_mode;
        } catch (error) {
            console.error('Failed to toggle ghost mode:', error);
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    ShidaApp.init();
});
