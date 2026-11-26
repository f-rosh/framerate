// FrameRate main JS
console.log("FrameRate loaded");

// Live movie search dropdown
document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('search-input');
    const dropdown = document.getElementById('search-dropdown');
    let searchTimer;
    let currentRequest = null;  // Track in-flight request

    if (!input || !dropdown) return;

    input.addEventListener('input', function() {
        clearTimeout(searchTimer);
        const query = this.value.trim();

        // Cancel any in-flight request
        if (currentRequest) {
            currentRequest.abort();
            currentRequest = null;
        }

        if (query.length < 2) {
            dropdown.style.display = 'none';
            return;
        }

        // Show "Searching..." immediately
        dropdown.innerHTML = '<div class="p-3 text-muted small">Searching...</div>';
        dropdown.style.display = 'block';

        // Debounce: wait 300ms after user stops typing
        searchTimer = setTimeout(() => {
            currentRequest = new AbortController();

            fetch(`/api/search/?q=${encodeURIComponent(query)}`, {
                signal: currentRequest.signal
            })
                .then(response => {
                    if (!response.ok) throw new Error('Network error');
                    return response.json();
                })
                .then(data => {
                    currentRequest = null;
                    if (data.results.length === 0) {
                        dropdown.innerHTML = '<div class="p-3 text-muted small">No results found</div>';
                    } else {
                        dropdown.innerHTML = data.results.map(m => `
                            <a href="/movie/${m.id}/" class="d-flex align-items-center p-2 text-decoration-none text-light border-bottom border-secondary">
                                ${m.poster ? `<img src="${m.poster}" width="40" height="60" class="me-2 rounded" style="object-fit: cover;">` : '<div class="me-2" style="width:40px;height:60px;"></div>'}
                                <div>
                                    <div class="small">${m.title}</div>
                                    <div class="text-muted" style="font-size: 11px;">${m.year || '—'}</div>
                                </div>
                            </a>
                        `).join('');
                    }
                    dropdown.style.display = 'block';
                })
                .catch(err => {
                    currentRequest = null;
                    // Don't hide on abort (user typed more)
                    if (err.name === 'AbortError') return;
                    // Show error but keep dropdown visible
                    dropdown.innerHTML = '<div class="p-3 text-muted small">Search error. Try again.</div>';
                    dropdown.style.display = 'block';
                });
        }, 300);
    });

    // Hide dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!input.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.style.display = 'none';
        }
    });

    // Show dropdown again when input is focused
    input.addEventListener('focus', function() {
        if (this.value.trim().length >= 2 && dropdown.innerHTML.trim()) {
            dropdown.style.display = 'block';
        }
    });
});