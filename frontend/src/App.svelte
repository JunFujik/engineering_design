<script>
  import { onMount } from 'svelte';
  import Login from './components/Login.svelte';
  import Register from './components/Register.svelte';
  import Dashboard from './components/Dashboard.svelte';
  import AdminDashboard from './components/AdminDashboard.svelte';

  let currentView = 'login';
  let isAuthenticated = false;
  let user = null;
  let token = null;

  onMount(() => {
    token = localStorage.getItem('token');
    console.log('Token from localStorage:', token ? 'exists' : 'not found');
    if (token) {
      checkAuth();
    }
  });

  async function checkAuth() {
    try {
      console.log('Checking authentication...');
      const response = await fetch('http://localhost:5000/api/profile', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      console.log('Auth check response status:', response.status);
      
      if (response.ok) {
        user = await response.json();
        isAuthenticated = true;
        console.log('Authentication successful:', user);
      } else {
        console.log('Authentication failed, clearing token');
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
    console.log('Login event received:', event.detail);
    token = event.detail.token;
    user = event.detail.user;
    localStorage.setItem('token', token);
    isAuthenticated = true;
  }

  function handleLogout() {
    console.log('Logging out...');
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
    {#if user && user.is_admin}
      <AdminDashboard {user} {token} on:logout={handleLogout} />
    {:else}
      <Dashboard {user} {token} on:logout={handleLogout} />
    {/if}
  {:else}
    {#if currentView === 'login'}
      <Login on:login={handleLogin} on:showRegister={showRegister} />
    {:else}
      <Register on:showLogin={showLogin} />
    {/if}
  {/if}
</main>

<style>
  main {
    padding: 20px;
    max-width: 800px;
    margin: 0 auto;
  }
  
  h1 {
    text-align: center;
    color: #333;
  }
</style>