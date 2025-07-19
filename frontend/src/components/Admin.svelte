<script>
  import { createEventDispatcher } from 'svelte';
  import { authAPI } from '../lib/api.js';

  const dispatch = createEventDispatcher();

  async function handleLogout() {
    try {
      await authAPI.logout();
      dispatch('logout');
    } catch (err) {
      console.error('Logout failed:', err);
    }
  }
</script>

<div class="admin-container">
  <header class="admin-header">
    <h1>管理者画面</h1>
    <button class="logout-btn" on:click={handleLogout}>ログアウト</button>
  </header>
  
  <div class="admin-content">
    <div class="welcome-card">
      <h2>ようこそ、管理者様</h2>
      <p>管理者専用の画面です。</p>
      <p>今後、管理機能がここに追加される予定です。</p>
    </div>
  </div>
</div>

<style>
  .admin-container {
    min-height: 100vh;
    background-color: #f8f9fa;
  }
  
  .admin-header {
    background: white;
    padding: 1rem 2rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .admin-header h1 {
    margin: 0;
    color: #333;
  }
  
  .logout-btn {
    background-color: #dc3545;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9em;
  }
  
  .logout-btn:hover {
    background-color: #c82333;
  }
  
  .admin-content {
    padding: 2rem;
    display: flex;
    justify-content: center;
  }
  
  .welcome-card {
    background: white;
    padding: 3rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    text-align: center;
    max-width: 500px;
  }
  
  .welcome-card h2 {
    color: #007bff;
    margin-bottom: 1rem;
  }
  
  .welcome-card p {
    color: #666;
    line-height: 1.6;
    margin-bottom: 1rem;
  }
</style>