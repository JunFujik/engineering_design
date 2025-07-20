<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { attendanceAPI, authAPI, userAPI } from '../lib/api.js';

  const dispatch = createEventDispatcher();

  let users = [];
  let attendances = [];
  let selectedUserId = '';
  let startDate = '';
  let endDate = '';
  let error = '';
  let loading = false;

  onMount(() => {
    loadUsers();
    fetchAttendance();
  });

  async function loadUsers() {
    try {
      const res = await userAPI.getAll();
      users = res.data;
    } catch (err) {
      error = 'ユーザーの取得に失敗しました';
    }
  }

  async function fetchAttendance() {
    loading = true;
    error = '';
    try {
      const params = {};
      if (selectedUserId) params.user_id = selectedUserId;
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;

      const res = await attendanceAPI.getAll(params);
      attendances = res.data;
    } catch (err) {
      error = '出勤データの取得に失敗しました';
    } finally {
      loading = false;
    }
  }

  function formatDateTime(dt) {
    if (!dt) return '—';
    return new Date(dt).toLocaleString('ja-JP');
  }

  function formatDate(dt) {
    if (!dt) return '—';
    return new Date(dt).toLocaleDateString('ja-JP');
  }

  function calculateWorkHours(checkIn, checkOut) {
    if (!checkIn || !checkOut) return '-';
    const start = new Date(checkIn);
    const end = new Date(checkOut);
    const diff = end - start;
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    return `${hours}時間${minutes}分`;
  }

  async function handleLogout() {
    try {
      await authAPI.logout();
      dispatch('logout');
      location.href = '/';
    } catch (err) {
      console.error('ログアウト失敗:', err);
    }
  }
</script>

<div class="staff-container">
  <header class="staff-header">
    <h1>連絡員画面</h1>
    <button class="logout-btn" on:click={handleLogout}>ログアウト</button>
  </header>

  <main class="staff-content">
    <h2>勤怠記録一覧</h2>

    {#if error}
      <p class="error">{error}</p>
    {/if}

    <div class="filters">
      <div class="form-group">
        <label for="filter-user">ユーザー</label>
        <select id="filter-user" bind:value={selectedUserId} on:change={fetchAttendance}>
          <option value="">全ユーザー</option>
          {#each users as user}
            <option value={user.id}>{user.name}</option>
          {/each}
        </select>
      </div>

      <div class="form-group">
        <label for="start-date">開始日</label>
        <input id="start-date" type="date" bind:value={startDate} on:change={fetchAttendance} />
      </div>

      <div class="form-group">
        <label for="end-date">終了日</label>
        <input id="end-date" type="date" bind:value={endDate} on:change={fetchAttendance} />
      </div>
    </div>

    {#if loading}
      <p>読み込み中...</p>
    {:else if attendances.length === 0}
      <p>出勤記録がありません。</p>
    {:else}
      <table>
        <thead>
          <tr>
            <th>日付</th>
            <th>ユーザー</th>
            <th>出勤時刻</th>
            <th>退勤時刻</th>
            <th>勤務時間</th>
          </tr>
        </thead>
        <tbody>
          {#each attendances as record}
            <tr>
              <td>{formatDate(record.date)}</td>
              <td>{record.user.name}</td>
              <td>{formatDateTime(record.check_in)}</td>
              <td>{formatDateTime(record.check_out)}</td>
              <td>{calculateWorkHours(record.check_in, record.check_out)}</td>
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

  .filters {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .form-group label {
    display: block;
    margin-bottom: 0.25rem;
    font-weight: bold;
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
    margin-top: 1rem;
  }
</style>
