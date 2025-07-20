<script>
  import { onMount } from 'svelte';
  import QRScanner from './components/QRScanner.svelte';
  import MakeUpClassRequest from './components/MakeUpClassRequest.svelte';
  import Login from './components/Login.svelte';
  import StaffLogin from './components/StaffLogin.svelte';
  import Admin from './components/Admin.svelte';
  import Staff from './components/staff.svelte';
  import { authAPI } from './lib/api.js';

  let activeTab = 'qr-scan';
  let currentRoute = 'home';
  let isLoggedIn = false;
  let staffLoggedIn = false;
  let showLogin = false;
  let showStaffLogin = false;

  const tabs = [
    { id: 'qr-scan', label: 'QRコード読取' },
    { id: 'makeup', label: '補講申請' }
  ];

  onMount(() => {
    checkAuthStatus();
    const path = window.location.pathname;
    if (path === '/admin') {
      currentRoute = 'admin';
    } else if (path === '/staff') {
      currentRoute = 'staff';
    }
  });

  async function checkAuthStatus() {
    try {
      const response = await authAPI.getStatus();
      isLoggedIn = response.data.logged_in;
      staffLoggedIn = response.data.staff_logged_in;
    } catch (err) {
      console.error('Auth status check failed:', err);
      isLoggedIn = false;
      staffLoggedIn = false;
    }
  }

  function handleLoginSuccess() {
    isLoggedIn = true;
    showLogin = false;
    currentRoute = 'admin';
    window.history.pushState({}, '', '/admin');
  }

  function handleStaffLoginSuccess() {
    console.log('[✅ イベント受信] staff-login-success');
    staffLoggedIn = true;
    showStaffLogin = false;
    currentRoute = 'staff';
    window.history.pushState({}, '', '/staff');
  }

  function handleLoginCancel() {
    showLogin = false;
    showStaffLogin = false;
  }

  function handleLogout() {
    isLoggedIn = false;
    staffLoggedIn = false;
    currentRoute = 'home';
    window.history.pushState({}, '', '/');
  }
</script>

{#if currentRoute === 'admin'}
  <Admin on:logout={handleLogout} />
{:else if currentRoute === 'staff'}
  <Staff on:logout={handleLogout} />
{:else}
  <main>
    <header>
      <h1>勤怠管理システム</h1>
      <div class="auth-section">
        {#if isLoggedIn}
          <span class="admin-status">管理者でログイン中</span>
          <button class="admin-btn" on:click={() => { currentRoute = 'admin'; window.history.pushState({}, '', '/admin'); }}>
            管理者画面
          </button>
          <button class="logout-btn" on:click={handleLogout}>ログアウト</button>
        {:else if staffLoggedIn}
          <span class="admin-status">連絡員でログイン中</span>
          <button class="admin-btn" on:click={() => { currentRoute = 'staff'; window.history.pushState({}, '', '/staff'); }}>
            連絡員画面
          </button>
          <button class="logout-btn" on:click={handleLogout}>ログアウト</button>
        {:else}
          <button class="login-btn" on:click={() => showLogin = true}>管理者ログイン</button>
          <button class="login-btn" on:click={() => showStaffLogin = true}>連絡員ログイン</button>
        {/if}
      </div>
    </header>

    <div class="tab-buttons">
      {#each tabs as tab}
        <button 
          class="tab-button" 
          class:active={activeTab === tab.id}
          on:click={() => activeTab = tab.id}
        >
          {tab.label}
        </button>
      {/each}
    </div>

    <div class="tab-content">
      {#if activeTab === 'qr-scan'}
        <QRScanner />
      {:else if activeTab === 'makeup'}
        <MakeUpClassRequest />
      {/if}
    </div>

    {#if showLogin}
      <Login on:login-success={handleLoginSuccess} on:cancel={handleLoginCancel} />
    {/if}

    {#if showStaffLogin}
      <StaffLogin on:staff-login-success={handleStaffLoginSuccess} on:cancel={handleLoginCancel} />
    {/if}
  </main>
{/if}

<style>
  main {
    text-align: center;
  }

  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    padding: 0 1rem;
  }

  h1 {
    color: #333;
    margin: 0;
  }

  .auth-section {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .admin-status {
    color: #28a745;
    font-weight: 500;
    font-size: 0.9em;
  }

  .login-btn, .logout-btn, .admin-btn {
    padding: 0.5rem 1rem;
    font-size: 0.9em;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    color: white;
  }

  .login-btn {
    background-color: #007bff;
  }

  .admin-btn {
    background-color: #28a745;
  }

  .logout-btn {
    background-color: #dc3545;
  }

  .login-btn:hover {
    background-color: #0056b3;
  }

  .admin-btn:hover {
    background-color: #218838;
  }

  .logout-btn:hover {
    background-color: #c82333;
  }

  .tab-content {
    text-align: left;
  }
</style>