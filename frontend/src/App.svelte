<script>
  import { onMount } from 'svelte';
  import Login from './components/Login.svelte';
  import Register from './components/Register.svelte';
  import Dashboard from './components/Dashboard.svelte';

  let currentView = 'login';
  let isAuthenticated = false;
  let user = null;
  let token = null;

  onMount(() => {
    token = localStorage.getItem('token');
    if (token) {
      checkAuth();
    }
  });

  async function checkAuth() {
    try {
      const response = await fetch('http://localhost:5000/api/profile', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        user = await response.json();
        isAuthenticated = true;
      } else {
        localStorage.removeItem('token');
        token = null;
        isAuthenticated = false;
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('token');
      token = null;
      isAuthenticated = false;
    }
  }

  function handleLogin(event) {
    token = event.detail.token;
    user = event.detail.user;
    localStorage.setItem('token', token);
    isAuthenticated = true;
  }

  function handleLogout() {
    localStorage.removeItem('token');
    token = null;
    user = null;
    isAuthenticated = false;
    currentView = 'login';
  }

  function showLogin() {
    currentView = 'login';
  }

  function showRegister() {
    currentView = 'register';
  }
</script>

<main>
  <h1>勤怠管理システム</h1>
  
  {#if isAuthenticated}
    <Dashboard {user} {token} on:logout={handleLogout} />
  {:else}
    {#if currentView === 'login'}
      <Login on:login={handleLogin} on:showRegister={showRegister} />
    {:else}
      <Register on:showLogin={showLogin} />
    {/if}
  {/if}
</main>