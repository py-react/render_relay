// Live Reload Client for KiwiJs
// Connects to backend Live Reload WebSocket and handles module updates

(function() {
  let socket = null;
  let reconnectAttempts = 0;
  const maxReconnectAttempts = 10;
  const reconnectDelay = 3000; // 3 seconds

  // CSS update handling
  function handleCssUpdate() {
    // Get all stylesheet links that might be affected
    const links = document.querySelectorAll('link[rel="stylesheet"]');
    links.forEach(link => {
      // Skip if it's not a KiwiJs managed stylesheet
      // For now, we'll reload all CSS - can be optimized later
      const href = link.href;
      if (href && !href.includes('chrome://')) {
        // Create a new link element with the same href but with a timestamp
        const newLink = document.createElement('link');
        newLink.rel = 'stylesheet';
        newLink.href = href + '?t=' + Date.now();
        
        // Replace the old link
        link.parentNode.insertBefore(newLink, link.nextSibling);
        
        // Remove the old link after a short delay to avoid flashing
        setTimeout(() => {
          link.remove();
        }, 50);
      }
    });
  }

  // JS update handling
  function handleJsUpdate() {
    // For JS updates, we'll do a full reload for now
    // This can be enhanced to use actual HMR if needed
    console.log('[KiwiJs LiveReload] Reloading page due to JS update');
    window.location.reload();
  }

  // Full reload handling
  function handleFullReload() {
    console.log('[KiwiJs LiveReload] Full reload requested');
    window.location.reload();
  }

  // WebSocket connection
  function connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/__live_reload`;
    
    console.log('[KiwiJs LiveReload] Connecting to:', wsUrl);
    
    socket = new WebSocket(wsUrl);
    
    socket.onopen = function() {
      console.log('[KiwiJs LiveReload] Connected to Live Reload server');
      reconnectAttempts = 0; // Reset on successful connection
    };
    
    socket.onmessage = function(event) {
      try {
        const data = JSON.parse(event.data);
        console.log('[KiwiJs LiveReload] Received:', data);
        
        switch (data.type) {
          case 'css_update':
            handleCssUpdate();
            break;
          case 'js_update':
            handleJsUpdate();
            break;
          case 'full_reload':
            handleFullReload();
            break;
          default:
            console.warn('[KiwiJs LiveReload] Unknown message type:', data.type);
        }
      } catch (e) {
        console.error('[KiwiJs LiveReload] Error parsing message:', e);
      }
    };
    
    socket.onclose = function() {
      console.log('[KiwiJs LiveReload] Disconnected from Live Reload server');
      scheduleReconnect();
    };
    
    socket.onerror = function(error) {
      console.error('[KiwiJs LiveReload] WebSocket error:', error);
      socket.close();
    };
  }
  
  // Schedule reconnection with exponential backoff
  function scheduleReconnect() {
    if (reconnectAttempts >= maxReconnectAttempts) {
      console.error('[KiwiJs LiveReload] Max reconnection attempts reached');
      return;
    }
    
    reconnectAttempts++;
    const delay = reconnectDelay * Math.pow(1.5, reconnectAttempts - 1); // Exponential backoff
    
    console.log(`[KiwiJs LiveReload] Scheduling reconnect in ${delay}ms (attempt ${reconnectAttempts}/${maxReconnectAttempts})`);
    
    setTimeout(connect, delay);
  }
  
  // Initialize connection when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', connect);
  } else {
    connect();
  }
  
  // Expose for debugging
  window.__kiwijsLiveReload = {
    socket: () => socket,
    reconnect: () => {
      if (socket) socket.close();
    }
  };
})();