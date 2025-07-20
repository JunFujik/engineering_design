<script>
  import { onMount } from 'svelte';
  import { makeupAPI } from '../lib/api.js';

  let makeupRequests = [];
  let error = '';
  let loading = true;
  let activeTab = 'pending';

  onMount(loadRequests);

  async function loadRequests() {
    loading = true;
    try {
      const res = await makeupAPI.getAll();
      makeupRequests = res.data;
    } catch (err) {
      error = '申請データの取得に失敗しました';
    } finally {
      loading = false;
    }
  }

  async function updateStatus(id, status) {
    try {
      await makeupAPI.update(id, { status }); // ← 前の安定してた実装
      await loadRequests(); // ← 反映を確実に
    } catch (err) {
      console.error('更新失敗:', err);
      error = 'ステータスの更新に失敗しました';
    }
  }

  $: filteredRequests = activeTab === 'pending'
    ? makeupRequests.filter(req => req.status?.trim().toLowerCase() === 'pending')
    : makeupRequests.filter(req => req.status && req.status !== 'pending');

  function formatDateTime(datetimeStr) {
    return new Date(datetimeStr).toLocaleString('ja-JP');
  }
</script>

<div class="card">
  <h2>補講申請 {activeTab === 'pending' ? '（未処理）' : '履歴'}</h2>

  <div class="tabs">
    <button on:click={() => activeTab = 'pending'} class:active={activeTab === 'pending'}>未処理</button>
    <button on:click={() => activeTab = 'history'} class:active={activeTab === 'history'}>履歴</button>
  </div>

  {#if error}
    <p class="error">{error}</p>
  {/if}

  {#if loading}
    <p>読み込み中...</p>
  {:else if filteredRequests.length === 0}
    <p>{activeTab === 'pending' ? '未処理の申請はありません。' : '履歴はありません。'}</p>
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
        {#each filteredRequests as req}
          <tr>
            <td>{formatDateTime(req.created_at)}</td>
            <td>{req.name}</td>
            <td>{req.subject}</td>
            <td>{req.original_date} {req.original_period}</td>
            <td>{req.new_date} {req.new_period}</td>
            <td>{req.status || '未処理'}</td>
            <td>
              {#if activeTab === 'pending'}
                <button on:click={() => {
                  if (confirm('本当に承認しますか？')) updateStatus(req.id, 'approved');
                }}>承認</button>
                <button on:click={() => {
                  if (confirm('本当に却下しますか？')) updateStatus(req.id, 'rejected');
                }}>却下</button>
              {:else if activeTab === 'history'}
                {#if req.status === 'approved'}
                  <button on:click={() => {
                    if (confirm('承認済み → 却下に戻しますか？')) updateStatus(req.id, 'rejected');
                  }}>却下に戻す</button>
                {:else if req.status === 'rejected'}
                  <button on:click={() => {
                    if (confirm('却下済み → 承認に戻しますか？')) updateStatus(req.id, 'approved');
                  }}>承認に戻す</button>
                {/if}
              {/if}
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
</div>

<style>
  .tabs {
    margin-bottom: 1rem;
  }
  .tabs button {
    margin-right: 0.5rem;
    padding: 0.5rem 1rem;
  }
  .tabs button.active {
    background-color: #007bff;
    color: white;
    font-weight: bold;
  }

  .error {
    color: red;
    margin-top: 1rem;
  }

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
</style>
