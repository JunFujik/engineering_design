<script>
  import { onMount } from 'svelte';
  import { paidLeaveAPI } from '../lib/api.js';

  let formData = {
    name: '',
    start_date: '',
    end_date: ''
  };

  let success = '';
  let error = '';
  let loading = false;
  let paidLeaveDays = 0;
  let requests = [];

  onMount(loadRequests);

  async function loadRequests() {
    try {
      const res = await paidLeaveAPI.getAll();
      requests = res.data;
    } catch (err) {
      console.error('取得失敗:', err);
    }
  }

  $: if (formData.start_date && formData.end_date) {
    const start = new Date(formData.start_date);
    const end = new Date(formData.end_date);
    if (end >= start) {
      paidLeaveDays = (end - start) / (1000 * 60 * 60 * 24) + 1;
    } else {
      paidLeaveDays = 0;
    }
  }

  async function handleSubmit() {
    success = '';
    error = '';
    loading = true;

    if (!formData.name || !formData.start_date || !formData.end_date) {
      error = 'すべての項目を入力してください';
      loading = false;
      return;
    }

    try {
      await paidLeaveAPI.create({ ...formData, days: paidLeaveDays });
      success = '有給申請を送信しました';
      formData = { name: '', start_date: '', end_date: '' };
      paidLeaveDays = 0;
      await loadRequests();
    } catch (err) {
      console.error(err);
      error = '申請に失敗しました';
    } finally {
      loading = false;
    }
  }
</script>

<div class="card">
  <h2>有給申請フォーム</h2>

  {#if success}<p class="success">{success}</p>{/if}
  {#if error}<p class="error">{error}</p>{/if}

  <form on:submit|preventDefault={handleSubmit}>
    <div class="form-group">
      <label>名前</label>
      <input type="text" bind:value={formData.name} required />
    </div>
    <div class="form-group">
      <label>開始日</label>
      <input type="date" bind:value={formData.start_date} required />
    </div>
    <div class="form-group">
      <label>終了日</label>
      <input type="date" bind:value={formData.end_date} required />
    </div>

    <p>有給日数: {paidLeaveDays} 日</p>

    <button type="submit" disabled={loading}>
      {loading ? '送信中...' : '申請する'}
    </button>
  </form>
</div>

{#if requests.length > 0}
  <div class="card">
    <h3>申請履歴</h3>
    <table>
      <thead>
        <tr>
          <th>名前</th>
          <th>開始日</th>
          <th>終了日</th>
          <th>日数</th>
          <th>申請日時</th>
        </tr>
      </thead>
      <tbody>
        {#each requests as req}
          <tr>
            <td>{req.name}</td>
            <td>{req.start_date}</td>
            <td>{req.end_date}</td>
            <td>{req.days_requested}</td>
            <td>{new Date(req.created_at).toLocaleString('ja-JP')}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
{/if}

<style>
  .card {
    padding: 1rem;
    background: white;
    border-radius: 8px;
    margin-top: 1rem;
  }

  .form-group {
    margin-bottom: 1rem;
  }

  .error {
    color: red;
  }

  .success {
    color: green;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
  }

  th, td {
    padding: 0.5rem;
    border: 1px solid #ccc;
  }

  th {
    background-color: #f1f1f1;
  }
</style>
