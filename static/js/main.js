// Modern Blog JavaScript - Complete Functionality

(function() {
    'use strict';

    // Initialize everything when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        initThemeToggle();
        initMobileMenu();
        initTableOfContents();
        initReadingTime();
        initSocialSharing();
        initCodeCopyButtons();
        initSmoothScroll();
        initPrism();
    });

    // Theme Toggle
    function initThemeToggle() {
        const themeToggle = document.getElementById('theme-toggle');
        const html = document.documentElement;
        
        // Get saved theme or default to light
        const savedTheme = localStorage.getItem('theme') || 'light';
        html.setAttribute('data-theme', savedTheme);
        updateThemeIcon(savedTheme);
        
        if (themeToggle) {
            themeToggle.addEventListener('click', function() {
                const currentTheme = html.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                
                html.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
                updateThemeIcon(newTheme);
            });
        }
    }

    function updateThemeIcon(theme) {
        const themeIcon = document.querySelector('.theme-icon');
        if (themeIcon) {
            themeIcon.textContent = theme === 'dark' ? '☀️' : '🌙';
        }
    }

    // Mobile Menu Toggle
    function initMobileMenu() {
        const menuToggle = document.getElementById('mobile-menu-toggle');
        const headerNav = document.getElementById('header-nav');
        
        if (menuToggle && headerNav) {
            menuToggle.addEventListener('click', function() {
                headerNav.classList.toggle('active');
                menuToggle.classList.toggle('active');
            });
            
            // Close menu when clicking outside
            document.addEventListener('click', function(e) {
                if (!headerNav.contains(e.target) && !menuToggle.contains(e.target)) {
                    headerNav.classList.remove('active');
                    menuToggle.classList.remove('active');
                }
            });
        }
    }

    // Table of Contents Generation
    function initTableOfContents() {
        const tocList = document.getElementById('toc-list');
        const tocToggle = document.getElementById('toc-toggle');
        const tocContent = document.getElementById('toc-content');
        const postContent = document.querySelector('.post-content-article');
        
        if (!tocList || !postContent) return;
        
        // Generate TOC from headings
        const headings = postContent.querySelectorAll('h1, h2, h3');
        if (headings.length === 0) {
            document.getElementById('post-toc').style.display = 'none';
            return;
        }
        
        headings.forEach((heading, index) => {
            // Add ID to heading if it doesn't have one
            if (!heading.id) {
                heading.id = `heading-${index}`;
            }
            
            const level = parseInt(heading.tagName.charAt(1));
            const li = document.createElement('li');
            li.className = `toc-level-${level}`;
            
            const a = document.createElement('a');
            a.href = `#${heading.id}`;
            a.textContent = heading.textContent;
            
            li.appendChild(a);
            tocList.appendChild(li);
        });
        
        // TOC Toggle
        if (tocToggle && tocContent) {
            tocToggle.addEventListener('click', function() {
                tocContent.classList.toggle('collapsed');
                tocToggle.textContent = tocContent.classList.contains('collapsed') ? '▶' : '▼';
            });
        }
        
        // Highlight active TOC item on scroll
        const observerOptions = {
            rootMargin: '-20% 0px -80% 0px',
            threshold: 0
        };
        
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const id = entry.target.id;
                    const tocLink = tocList.querySelector(`a[href="#${id}"]`);
                    if (tocLink) {
                        tocList.querySelectorAll('a').forEach(link => {
                            link.classList.remove('active');
                        });
                        tocLink.classList.add('active');
                    }
                }
            });
        }, observerOptions);
        
        headings.forEach(heading => observer.observe(heading));
    }

    // Reading Time Calculation
    function initReadingTime() {
        const readingTimeEl = document.getElementById('reading-time');
        const postContent = document.querySelector('.post-content-article');
        
        if (!readingTimeEl || !postContent) return;
        
        const text = postContent.textContent || postContent.innerText;
        const wordsPerMinute = 200;
        const wordCount = text.trim().split(/\s+/).length;
        const readingTime = Math.ceil(wordCount / wordsPerMinute);
        
        readingTimeEl.textContent = `⏱️ ${readingTime} min read`;
    }

    // Social Sharing
    function initSocialSharing() {
        const shareButtons = document.querySelectorAll('[data-share]');
        const currentUrl = window.location.href;
        const currentTitle = document.title;
        
        shareButtons.forEach(button => {
            button.addEventListener('click', function() {
                const platform = this.getAttribute('data-share');
                let shareUrl = '';
                
                switch(platform) {
                    case 'twitter':
                        shareUrl = `https://twitter.com/intent/tweet?url=${encodeURIComponent(currentUrl)}&text=${encodeURIComponent(currentTitle)}`;
                        window.open(shareUrl, '_blank', 'width=550,height=420');
                        break;
                    case 'facebook':
                        shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(currentUrl)}`;
                        window.open(shareUrl, '_blank', 'width=550,height=420');
                        break;
                    case 'linkedin':
                        shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(currentUrl)}`;
                        window.open(shareUrl, '_blank', 'width=550,height=420');
                        break;
                    case 'copy':
                        navigator.clipboard.writeText(currentUrl).then(() => {
                            const originalText = this.textContent;
                            this.textContent = '✓ Copied!';
                            setTimeout(() => {
                                this.textContent = originalText;
                            }, 2000);
                        }).catch(err => {
                            console.error('Failed to copy:', err);
                            alert('Failed to copy link. Please copy manually: ' + currentUrl);
                        });
                        break;
                }
            });
        });
    }

    // Code Copy Buttons
    function initCodeCopyButtons() {
        const codeBlocks = document.querySelectorAll('pre.code-block, pre[class*="language-"]');
        
        codeBlocks.forEach(pre => {
            // Check if button already exists
            if (pre.querySelector('.copy-code-btn')) return;
            
            const button = document.createElement('button');
            button.className = 'copy-code-btn';
            button.innerHTML = '📋 Copy';
            button.setAttribute('aria-label', 'Copy code');
            button.style.cssText = `
                position: absolute;
                top: 12px;
                right: 12px;
                padding: 6px 12px;
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 6px;
                color: rgba(255, 255, 255, 0.9);
                cursor: pointer;
                font-size: 0.75rem;
                transition: all 0.2s;
                z-index: 10;
                backdrop-filter: blur(10px);
            `;
            
            button.addEventListener('mouseenter', function() {
                this.style.background = 'rgba(255, 255, 255, 0.2)';
                this.style.color = 'white';
            });
            
            button.addEventListener('mouseleave', function() {
                this.style.background = 'rgba(255, 255, 255, 0.1)';
                this.style.color = 'rgba(255, 255, 255, 0.9)';
            });
            
            button.addEventListener('click', function() {
                const code = pre.querySelector('code') || pre;
                const text = code.textContent || code.innerText;
                
                navigator.clipboard.writeText(text).then(() => {
                    button.innerHTML = '✓ Copied!';
                    setTimeout(() => {
                        button.innerHTML = '📋 Copy';
                    }, 2000);
                }).catch(err => {
                    console.error('Failed to copy:', err);
                    button.innerHTML = '❌ Error';
                    setTimeout(() => {
                        button.innerHTML = '📋 Copy';
                    }, 2000);
                });
            });
            
            pre.style.position = 'relative';
            pre.appendChild(button);
        });
    }

    // Smooth Scroll for Anchor Links
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href === '#' || href === '') return;
                
                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    const headerOffset = 80;
                    const elementPosition = target.getBoundingClientRect().top;
                    const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                    
                    window.scrollTo({
                        top: offsetPosition,
                        behavior: 'smooth'
                    });
                }
            });
        });
    }

    // Initialize Prism.js
    function initPrism() {
        if (typeof Prism !== 'undefined') {
            Prism.highlightAll();
        }
    }

    // Header Scroll Effect
    window.addEventListener('scroll', function() {
        const header = document.getElementById('site-header');
        if (header) {
            if (window.scrollY > 50) {
                header.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
            } else {
                header.style.boxShadow = '0 1px 3px 0 rgba(0, 0, 0, 0.1)';
            }
        }
    });

    // Lazy Load Images
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        observer.unobserve(img);
                    }
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }

    // Search Enhancement
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('focus', function() {
            this.parentElement.style.borderColor = 'var(--color-primary)';
        });
        
        searchInput.addEventListener('blur', function() {
            this.parentElement.style.borderColor = '';
        });
    }

    // Newsletter Form
    const newsletterForm = document.getElementById('newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const emailInput = document.getElementById('newsletter-email');
            const messageDiv = document.getElementById('newsletter-message');
            const submitButton = newsletterForm.querySelector('button[type="submit"]');
            
            if (!emailInput || !messageDiv) return;
            
            const email = emailInput.value.trim();
            
            if (!email) {
                showNewsletterMessage('Please enter a valid email address.', 'error');
                return;
            }
            
            // Disable button
            submitButton.disabled = true;
            submitButton.textContent = 'Subscribing...';
            
            try {
                const response = await fetch('/api/newsletter', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email: email })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showNewsletterMessage(data.message || 'Successfully subscribed! Thank you.', 'success');
                    emailInput.value = '';
                } else {
                    showNewsletterMessage(data.message || 'An error occurred. Please try again.', 'error');
                }
            } catch (error) {
                showNewsletterMessage('An error occurred. Please try again later.', 'error');
            } finally {
                submitButton.disabled = false;
                submitButton.textContent = 'Subscribe';
            }
        });
    }
    
    function showNewsletterMessage(message, type) {
        const messageDiv = document.getElementById('newsletter-message');
        if (!messageDiv) return;
        
        messageDiv.textContent = message;
        messageDiv.className = `newsletter-message ${type}`;
        messageDiv.style.display = 'block';
        
        // Hide after 5 seconds
        setTimeout(() => {
            messageDiv.style.display = 'none';
        }, 5000);
    }

})();
