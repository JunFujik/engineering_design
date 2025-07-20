<script>
  import { createEventDispatcher } from 'svelte';
  import { attendanceAPI, authAPI } from '../lib/api.js';
  import { onMount } from 'svelte';

  const dispatch = createEventDispatcher();

  let attendances = [];
  let loading = true;
  let error = '';

  async function fetchAttendance() {
    loading = true;
    try {
      const res = await attendanceAPI.getAll(); // /api/staff/attendance を使うなら差し替え
      attendances = res.data;
    } catch (err) {
      error = err.response?.data?.error || '出勤データの取得に失敗しました';
    } finally {
      loading = false;
    }
  }

  async function handleLogout() {
    try {
      await authAPI.logout(); // そのまま admin と共用でOK
      dispatch('logout');
      location.href = '/'; // ログアウト後トップへ
    } catch (err) {
      console.error('ログアウト失敗:', err);
    }
  }

  onMount(fetchAttendance);
</script>

<div class="staff-container">
  <header class="staff-header">
    <h1>連絡員画面</h1>
    <button class="logout-btn" on:click={handleLogout}>ログアウト</button>
  </header>

  <main class="staff-content">
    <h2>出勤記録一覧</h2>

    {#if loading}
      <p>読み込み中...</p>
    {:else if error}
      <p class="error">{error}</p>
    {:else if attendances.length === 0}
      <p>出勤記録がありません。</p>
    {:else}
      <table>
        <thead>
          <tr>
            <th>氏名</th>
            <th>日付</th>
            <th>出勤時刻</th>
          </tr>
        </thead>
        <tbody>
          {#each attendances as record}
            <tr>
              <td>{record.user.name}</td>
              <td>{record.date}</td>
              <td>{record.check_in || '—'}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    {/if}
  </main>
</div>

<style>
  .staff-container {
    min-height: 100vh;
    background-color: #f8f9fa;
  }

  .staff-header {
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
  }

  .staff-content {
    padding: 2rem;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    margin-top: 1rem;
  }

  th, td {
    padding: 0.75rem;
    border: 1px solid #dee2e6;
    text-align: left;
  }

  th {
    background-color: #e9ecef;
  }

  .error {
    color: red;
  }
</style>
