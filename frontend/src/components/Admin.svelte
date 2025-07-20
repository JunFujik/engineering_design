<script>
  import { createEventDispatcher } from 'svelte';
  import { authAPI } from '../lib/api.js';
  import ExcelImporter from './ExcelImporter.svelte';

  const dispatch = createEventDispatcher();

  let activeTab = 'dashboard';

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
  
  <nav class="admin-nav">
    <button 
      class="nav-btn" 
      class:active={activeTab === 'dashboard'}
      on:click={() => activeTab = 'dashboard'}
    >
      ダッシュボード
    </button>
    <button 
      class="nav-btn" 
      class:active={activeTab === 'excel-import'}
      on:click={() => activeTab = 'excel-import'}
    >
      Excelインポート
    </button>
  </nav>
  
  <div class="admin-content">
    {#if activeTab === 'dashboard'}
      <div class="welcome-card">
        <h2>ようこそ、管理者様</h2>
        <p>管理者専用の画面です。</p>
        <div class="feature-list">
          <div class="feature-item">
            <h3>Excelインポート機能</h3>
            <p>HTML形式で保存されたExcelファイルから勤怠データを読み込むことができます。</p>
            <button on:click={() => activeTab = 'excel-import'}>
              Excelインポートを開く
            </button>
          </div>
        </div>
      </div>
    {:else if activeTab === 'excel-import'}
      <ExcelImporter />
    {/if}
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

  .admin-nav {
    background: white;
    padding: 0 2rem;
    border-bottom: 1px solid #dee2e6;
    display: flex;
    gap: 0;
  }

  .nav-btn {
    background: none;
    border: none;
    padding: 1rem 1.5rem;
    color: #6c757d;
    border-bottom: 3px solid transparent;
    cursor: pointer;
    font-size: 1em;
    transition: all 0.2s;
  }

  .nav-btn:hover {
    color: #007bff;
    background-color: #f8f9fa;
  }

  .nav-btn.active {
    color: #007bff;
    border-bottom-color: #007bff;
    font-weight: 600;
  }
  
  .admin-content {
    padding: 2rem;
  }
  
  .welcome-card {
    background: white;
    padding: 3rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    text-align: center;
    max-width: 800px;
    margin: 0 auto;
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

  .feature-list {
    margin-top: 2rem;
    text-align: left;
  }

  .feature-item {
    background: #f8f9fa;
    padding: 1.5rem;
    border-radius: 6px;
    margin-bottom: 1rem;
  }

  .feature-item h3 {
    color: #495057;
    margin-top: 0;
    margin-bottom: 0.5rem;
  }

  .feature-item p {
    margin-bottom: 1rem;
  }

  .feature-item button {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9em;
  }

  .feature-item button:hover {
    background-color: #0056b3;
  }
</style>