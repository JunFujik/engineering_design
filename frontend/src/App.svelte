<script>
  import { onMount } from 'svelte';
  import UserManagement from './components/UserManagement.svelte';
  import QRGenerator from './components/QRGenerator.svelte';
  import QRScanner from './components/QRScanner.svelte';
  import AttendanceList from './components/AttendanceList.svelte';
  import MakeUpClassRequest from './components/MakeUpClassRequest.svelte';
  import Login from './components/Login.svelte';
  import Admin from './components/Admin.svelte';
  import { authAPI } from './lib/api.js';

  let activeTab = 'users';
  let currentRoute = 'home';
  let isLoggedIn = false;
  let showLogin = false;

  const tabs = [
    { id: 'users', label: 'ユーザー管理' },
    { id: 'qr-generate', label: 'QRコード生成' },
    { id: 'qr-scan', label: 'QRコード読取' },
    { id: 'attendance', label: '勤怠記録' },
    { id: 'makeup', label: '補講申請' }
  ];

  onMount(() => {
    checkAuthStatus();
    // 簡単なルーティング処理
    const path = window.location.pathname;
    if (path === '/admin') {
      currentRoute = 'admin';
    }
  });

  async function checkAuthStatus() {
    try {
      const response = await authAPI.getStatus();
      isLoggedIn = response.data.logged_in;
    } catch (err) {
      console.error('Auth status check failed:', err);
      isLoggedIn = false;
    }
  }

  function handleLoginSuccess() {
    isLoggedIn = true;
    showLogin = false;
    // 管理者ページに遷移
    currentRoute = 'admin';
    window.history.pushState({}, '', '/admin');
  }

  function handleLoginCancel() {
    showLogin = false;
  }

  function handleLogout() {
    isLoggedIn = false;
    currentRoute = 'home';
    window.history.pushState({}, '', '/');
  }

  function goHome() {
    currentRoute = 'home';
    window.history.pushState({}, '', '/');
  }
</script>

{#if currentRoute === 'admin'}
  <Admin on:logout={handleLogout} />
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
        {:else}
          <button class="login-btn" on:click={() => showLogin = true}>管理者ログイン</button>
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
      {#if activeTab === 'users'}
        <UserManagement />
      {:else if activeTab === 'qr-generate'}
        <QRGenerator />
      {:else if activeTab === 'qr-scan'}
        <QRScanner />
      {:else if activeTab === 'attendance'}
        <AttendanceList />
      {:else if activeTab === 'makeup'}
        <MakeUpClassRequest />
      {/if}
    </div>

    {#if showLogin}
      <Login on:login-success={handleLoginSuccess} on:cancel={handleLoginCancel} />
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