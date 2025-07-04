<script>
  import UserManagement from './components/UserManagement.svelte';
  import QRGenerator from './components/QRGenerator.svelte';
  import QRScanner from './components/QRScanner.svelte';
  import AttendanceList from './components/AttendanceList.svelte';

  let activeTab = 'users';

  const tabs = [
    { id: 'users', label: 'ユーザー管理' },
    { id: 'qr-generate', label: 'QRコード生成' },
    { id: 'qr-scan', label: 'QRコード読取' },
    { id: 'attendance', label: '勤怠記録' }
  ];
</script>

<main>
  <h1>勤怠管理システム</h1>
  
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
    {/if}
  </div>
</main>

<style>
  main {
    text-align: center;
  }

  h1 {
    color: #333;
    margin-bottom: 2rem;
  }

  .tab-content {
    text-align: left;
  }
</style>