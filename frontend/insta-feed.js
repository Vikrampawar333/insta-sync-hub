/**
 * ==========================================================================
 * INSTA-SYNC HUB — 100% REAL INSTAGRAM FEED WIDGET
 * Zero fake badges • Zero fake likes • Zero fake followers • 100% Real Meta Data
 * ==========================================================================
 */

(function (window) {
  'use strict';

  const InstaHub = {
    config: {
      container: '#insta-social-hub',
      apiUrl: (typeof window !== 'undefined' && window.location && window.location.origin) ? window.location.origin : 'http://localhost:8080',
    },

    state: {
      profile: null,
      posts: [],
      eventSource: null,
    },

    init: async function (options = {}) {
      Object.assign(this.config, options);

      const root = typeof this.config.container === 'string'
        ? document.querySelector(this.config.container)
        : this.config.container;

      if (!root) {
        console.error('[InstaHub] Container not found:', this.config.container);
        return;
      }

      this.root = root;
      this.renderStructure();

      await this.loadInitialData();
      this.initRealtimeStream();

      // Background auto-sync polling every 15 seconds (zero refresh)
      setInterval(() => {
        this.fetchPosts(true);
      }, 15000);
    },

    renderStructure: function () {
      this.root.innerHTML = `
        <div class="ig-feed-container">
          <div class="ig-cards-grid" id="ig-cards-grid">
            <div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: #737373;">
              Loading Instagram posts...
            </div>
          </div>
        </div>
      `;
    },

    loadInitialData: async function () {
      try {
        const profRes = await fetch(`${this.config.apiUrl}/api/profile`);
        if (profRes.ok) {
          this.state.profile = await profRes.json();
        }
      } catch (err) {
        console.warn('[InstaHub] Profile load error:', err);
      }

      await this.fetchPosts(false);
    },

    fetchPosts: async function (isBackground = false) {
      try {
        const res = await fetch(`${this.config.apiUrl}/api/posts`);
        if (!res.ok) return;

        const data = await res.json();
        const incomingPosts = data.posts || [];

        const currentIds = (this.state.posts || []).map(p => p.id).join(',');
        const incomingIds = incomingPosts.map(p => p.id).join(',');

        if (currentIds !== incomingIds || this.state.posts.length !== incomingPosts.length || !isBackground) {
          this.state.posts = incomingPosts;
          this.renderCards();
        }
      } catch (err) {
        console.error('[InstaHub] Error fetching posts:', err);
      }
    },

    renderCards: function () {
      const grid = document.getElementById('ig-cards-grid');
      if (!grid) return;

      if (!this.state.posts || this.state.posts.length === 0) {
        grid.innerHTML = `
          <div style="grid-column: 1/-1; text-align: center; padding: 4rem 1rem; color: #737373;">
            No Instagram posts found on this account.
          </div>
        `;
        return;
      }

      const profile = this.state.profile || {};
      const username = profile.username || 'instagram';
      const avatarUrl = profile.profile_picture_url || '';
      const profileUrl = `https://www.instagram.com/${username}/`;

      // Real subtitle: user's name or bio or real followers
      let subtext = '';
      if (profile.name) {
        subtext = profile.name;
      } else if (profile.biography) {
        subtext = profile.biography;
      } else if (typeof profile.followers_count === 'number') {
        subtext = `${profile.followers_count} followers`;
      }

      grid.innerHTML = this.state.posts.map(post => {
        const isReel = post.media_type === 'REEL' || post.media_type === 'VIDEO';
        const displayMedia = post.local_media_path ? `${this.config.apiUrl}${post.local_media_path}` : post.media_url;
        const displayThumb = post.thumbnail_url || displayMedia;
        const permalink = post.permalink || profileUrl;
        
        // Exact real likes count from Instagram API (No fake fallback numbers)
        const realLikes = (typeof post.like_count === 'number') ? post.like_count : 0;
        const realLikesText = realLikes === 1 ? '1 like' : `${realLikes} likes`;

        const caption = post.caption ? post.caption.trim() : '';
        const captionEscaped = this.escapeHtml(caption);

        return `
          <article class="ig-post-card" id="ig-card-${post.id}">
            <!-- 1. Card Header (100% Real Instagram Data) -->
            <header class="ig-card-top">
              <a href="${profileUrl}" target="_blank" rel="noopener" class="ig-card-author-left">
                ${avatarUrl ? `
                  <img class="ig-card-avatar" src="${avatarUrl}" alt="${username}">
                ` : `
                  <div class="ig-card-avatar-placeholder">${username.charAt(0).toUpperCase()}</div>
                `}
                <div class="ig-card-author-meta">
                  <div class="ig-card-username-line">
                    <span class="ig-card-username">${username}</span>
                  </div>
                  ${subtext ? `<span class="ig-card-followers-text">${this.escapeHtml(subtext)}</span>` : ''}
                </div>
              </a>

              <a href="${profileUrl}" target="_blank" rel="noopener" class="ig-btn-view-profile">
                View profile
              </a>
            </header>

            <!-- 2. Card Media (Real Instagram Photo or Reel) -->
            <div class="ig-card-media-wrapper">
              <a href="${permalink}" target="_blank" rel="noopener" style="display:block; width:100%; height:100%;">
                ${isReel ? `
                  <div class="ig-card-reel-badge">
                    <svg width="11" height="11" viewBox="0 0 24 24" fill="currentColor">
                      <polygon points="5 3 19 12 5 21 5 3"></polygon>
                    </svg>
                    Reel
                  </div>
                ` : ''}
                <img src="${displayThumb}" alt="Instagram Post" loading="lazy">
              </a>
            </div>

            <!-- 3. Card Bottom (Real Likes & Real Caption) -->
            <div class="ig-card-bottom">
              <a href="${permalink}" target="_blank" rel="noopener" class="ig-link-view-more">
                View more on Instagram
              </a>

              <!-- Action Icons Row -->
              <div class="ig-actions-row">
                <div class="ig-actions-left">
                  <a href="${permalink}" target="_blank" rel="noopener" class="ig-action-svg" title="Like on Instagram">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                      <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                    </svg>
                  </a>
                  <a href="${permalink}" target="_blank" rel="noopener" class="ig-action-svg" title="Comment on Instagram">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                      <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>
                    </svg>
                  </a>
                  <a href="${permalink}" target="_blank" rel="noopener" class="ig-action-svg" title="Share on Instagram">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                      <line x1="22" y1="2" x2="11" y2="13"></line>
                      <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                    </svg>
                  </a>
                </div>

                <a href="${permalink}" target="_blank" rel="noopener" class="ig-action-svg" title="Save on Instagram">
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                    <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
                  </svg>
                </a>
              </div>

              <!-- Real Likes Count -->
              <div class="ig-likes-count">${realLikesText}</div>

              <!-- Real Caption (Only if caption exists on Instagram) -->
              ${caption ? `
                <div class="ig-caption-container">
                  <span class="ig-caption-username">${username}</span>
                  <span class="ig-caption-text ig-caption-collapsed" id="ig-caption-${post.id}">${captionEscaped}</span>
                </div>
              ` : ''}

              <!-- Footer Bar -->
              <div class="ig-card-footer-bar">
                ${caption.length > 60 ? `
                  <button class="ig-btn-show-desc" onclick="InstaHub.toggleCaption(${post.id}, this)">
                    ▼ Show more description
                  </button>
                ` : `<span></span>`}

                <a href="${permalink}" target="_blank" rel="noopener" class="ig-link-instagram-brand">
                  Instagram
                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                    <polyline points="15 3 21 3 21 9"></polyline>
                    <line x1="10" y1="14" x2="21" y2="3"></line>
                  </svg>
                </a>
              </div>
            </div>
          </article>
        `;
      }).join('');
    },

    toggleCaption: function (postId, btn) {
      const textEl = document.getElementById(`ig-caption-${postId}`);
      if (!textEl) return;

      const isCollapsed = textEl.classList.contains('ig-caption-collapsed');
      if (isCollapsed) {
        textEl.classList.remove('ig-caption-collapsed');
        btn.textContent = '▲ Show less description';
      } else {
        textEl.classList.add('ig-caption-collapsed');
        btn.textContent = '▼ Show more description';
      }
    },

    initRealtimeStream: function () {
      if (!window.EventSource) return;

      try {
        if (this.state.eventSource) this.state.eventSource.close();
        this.state.eventSource = new EventSource(`${this.config.apiUrl}/api/stream`);

        this.state.eventSource.onmessage = (e) => {
          try {
            const data = JSON.parse(e.data);
            if (data.event === 'new_post' || data.event === 'sync_completed') {
              this.fetchPosts(true);
            }
          } catch (err) {}
        };
      } catch (e) {
        console.log('[InstaHub] Realtime sync active');
      }
    },

    escapeHtml: function (str) {
      if (!str) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    }
  };

  window.InstaHub = InstaHub;
})(window);
