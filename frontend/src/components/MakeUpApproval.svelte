<script>
  import { onMount } from 'svelte';
  import { makeupAPI } from '../lib/api.js';

  let makeupRequests = [];
  let error = '';
  let loading = false;

  onMount(loadRequests);

  async function loadRequests() {
    loading = true;
    try {
      const res = await makeupAPI.getAll();
      makeupRequests = res.data;
    } catch (err) {
      error = '補講申請の取得に失敗しました';
    } finally {
      loading = false;
    }
  }

  async function updateStatus(id, status) {
    try {
      await makeupAPI.update(id, { status });
      await loadRequests(); // リロードして反映
    } catch (err) {
      console.error('更新失敗:', err);
      error = '更新に失敗しました';
    }
  }

  function formatDateTime(datetime) {
    return new Date(datetime).toLocaleString('ja-JP');
  }
</script>

<div class="card">
  <h2>補講申請 承認画面</h2>

  {#if error}
    <p class="error">{error}</p>
  {/if}

  {#if loading}
    <p>読み込み中...</p>
  {:else if makeupRequests.length === 0}
    <p>補講申請はありません。</p>
  {:else}
    <table>
      <thead>
        <tr>
          <th>申請日時</th>
          <th>名前</th>
          <th>科目</th>
          <th>変更前</th>
          <th>変更後</th>
          <th>ステータス</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        {#each makeupRequests as req}
          <tr>
            <td>{formatDateTime(req.created_at)}</td>
            <td>{req.name}</td>
            <td>{req.subject}</td>
            <td>{req.original_date} {req.original_period}</td>
            <td>{req.new_date} {req.new_period}</td>
            <td>{req.status || '未処理'}</td>
            <td>
              {#if req.status !== 'approved'}
                <button
  on:click={() => {
    if (confirm('本当に承認しますか？')) {
      updateStatus(req.id, 'approved');
    }
  }}
>
  承認
</button>
              {/if}
              {#if req.status !== 'rejected'}
                <button
  on:click={() => {
    if (confirm('本当に却下しますか？')) {
      updateStatus(req.id, 'rejected');
    }
  }}
>
  却下
</button>
              {/if}
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
</div>

<style>
  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
    background: white;
  }

  th, td {
    padding: 0.75rem;
    border: 1px solid #ddd;
    text-align: left;
  }

  th {
    background-color: #f1f1f1;
  }

  button {
    margin-right: 0.5rem;
    padding: 0.4rem 0.8rem;
    font-size: 0.9em;
  }

  .error {
    color: red;
    margin-top: 1rem;
  }
</style>
