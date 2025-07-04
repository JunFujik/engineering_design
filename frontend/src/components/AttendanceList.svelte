<script>
  import { onMount } from 'svelte';
  import { userAPI, attendanceAPI } from '../lib/api.js';

  let users = [];
  let attendances = [];
  let selectedUserId = '';
  let startDate = '';
  let endDate = '';
  let error = '';
  let loading = false;

  onMount(() => {
    loadUsers();
    loadAttendances();
  });

  async function loadUsers() {
    try {
      const response = await userAPI.getAll();
      users = response.data;
    } catch (err) {
      error = 'ユーザーの読み込みに失敗しました';
    }
  }

  async function loadAttendances() {
    error = '';
    loading = true;
    
    try {
      const params = {};
      if (selectedUserId) params.user_id = selectedUserId;
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      
      const response = await attendanceAPI.getAll(params);
      attendances = response.data;
    } catch (err) {
      error = '勤怠記録の読み込みに失敗しました';
    } finally {
      loading = false;
    }
  }

  function formatDateTime(dateString) {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleString('ja-JP');
  }

  function formatDate(dateString) {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('ja-JP');
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
</script>

<div class="card">
  <h2>勤怠記録一覧</h2>
  
  {#if error}
    <p class="error">{error}</p>
  {/if}
  
  <div class="filters">
    <div class="form-group">
      <label for="filter-user">ユーザー</label>
      <select id="filter-user" bind:value={selectedUserId} on:change={loadAttendances}>
        <option value="">全ユーザー</option>
        {#each users as user}
          <option value={user.id}>{user.name}</option>
        {/each}
      </select>
    </div>
    
    <div class="form-group">
      <label for="start-date">開始日</label>
      <input 
        id="start-date"
        type="date" 
        bind:value={startDate}
        on:change={loadAttendances}
      />
    </div>
    
    <div class="form-group">
      <label for="end-date">終了日</label>
      <input 
        id="end-date"
        type="date" 
        bind:value={endDate}
        on:change={loadAttendances}
      />
    </div>
  </div>
  
  {#if loading}
    <p>読み込み中...</p>
  {:else if attendances.length === 0}
    <p>勤怠記録がありません</p>
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
        {#each attendances as attendance}
          <tr>
            <td>{formatDate(attendance.date)}</td>
            <td>{attendance.user.name}</td>
            <td>{formatDateTime(attendance.check_in)}</td>
            <td>{formatDateTime(attendance.check_out)}</td>
            <td>{calculateWorkHours(attendance.check_in, attendance.check_out)}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
</div>

<style>
  .filters {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
  }
  
  .filters .form-group {
    margin-bottom: 0;
  }
</style>