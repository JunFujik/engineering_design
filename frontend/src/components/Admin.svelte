<script>
  import { createEventDispatcher } from 'svelte';
  import { authAPI } from '../lib/api.js';
  import UserManagement from './UserManagement.svelte';
  import QRGenerator from './QRGenerator.svelte';
  import QRScanner from './QRScanner.svelte';
  import AttendanceList from './AttendanceList.svelte';
  import MakeUpApproval from './MakeUpApproval.svelte';
  import ExcelImporter from './ExcelImporter.svelte';
  import AttendanceTableViewer from './AttendanceTableViewer.svelte';

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
    <button class="nav-btn" class:active={activeTab === 'dashboard'} on:click={() => activeTab = 'dashboard'}>
      ダッシュボード
    </button>
    <button class="nav-btn" class:active={activeTab === 'user-management'} on:click={() => activeTab = 'user-management'}>
      ユーザー管理
    </button>
    <button class="nav-btn" class:active={activeTab === 'qr-generate'} on:click={() => activeTab = 'qr-generate'}>
      QRコード生成
    </button>
    <button class="nav-btn" class:active={activeTab === 'qr-scan'} on:click={() => activeTab = 'qr-scan'}>
      QRコード読取
    </button>
    <button class="nav-btn" class:active={activeTab === 'attendance'} on:click={() => activeTab = 'attendance'}>
      勤怠記録
    </button>
    <button class="nav-btn" class:active={activeTab === 'makeup-approval'} on:click={() => activeTab = 'makeup-approval'}>
      補講申請承認
    </button>
    <button class="nav-btn" class:active={activeTab === 'excel-import'} on:click={() => activeTab = 'excel-import'}>
      Excelインポート
    </button>
    <button class="nav-btn" class:active={activeTab === 'attendance-tables'} on:click={() => activeTab = 'attendance-tables'}>
      出勤簿表示
    </button>
  </nav>

  <div class="admin-content">
    {#if activeTab === 'dashboard'}
      <div class="welcome-card">
        <h2>ようこそ、管理者様</h2>
        <p>管理者専用の機能を利用できます。</p>
      </div>
    {:else if activeTab === 'user-management'}
      <UserManagement />
    {:else if activeTab === 'qr-generate'}
      <QRGenerator />
    {:else if activeTab === 'qr-scan'}
      <QRScanner />
    {:else if activeTab === 'attendance'}
      <AttendanceList />
    {:else if activeTab === 'makeup-approval'}
      <MakeUpApproval />
    {:else if activeTab === 'excel-import'}
      <ExcelImporter />
    {:else if activeTab === 'attendance-tables'}
      <AttendanceTableViewer />
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
    flex-wrap: wrap;
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
</style>
