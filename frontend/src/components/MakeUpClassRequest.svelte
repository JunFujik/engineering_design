<script>
  import { onMount } from 'svelte';
  import { makeupAPI } from '../lib/api.js'; // 正しいAPIをインポート

  let formData = {
    name: '',
    subject: '',
    original_date: '',
    original_period: '',
    new_date: '',
    new_period: ''
  };

  let success = '';
  let error = '';
  let loading = false;
  let makeupRequests = [];
  let showRequests = false;

  // 選択肢のダミーデータ
  const periods = ['1限', '2限', '3限', '4限', '5限'];
  let dates = [];

  onMount(() => {
    // 日付の選択肢を生成（例：今日から30日後まで）
    const today = new Date();
    for (let i = 0; i < 30; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() + i);
      dates.push(date.toISOString().split('T')[0]);
    }
    loadMakeupRequests();
  });

  async function loadMakeupRequests() {
    try {
      const response = await makeupAPI.getAll();
      makeupRequests = response.data;
    } catch (err) {
      console.error('補講申請の読み込みエラー:', err);
    }
  }

  async function handleSubmit() {
    error = '';
    success = '';
    loading = true;

    // 簡単なバリデーション
    for (const key in formData) {
      if (!formData[key]) {
        error = 'すべての項目を入力してください。';
        loading = false;
        return;
      }
    }

    try {
      console.log('送信データ:', formData); // デバッグ用
      await makeupAPI.create(formData);
      success = '補講申請を送信しました。';
      // フォームをリセット
      formData = {
        name: '',
        subject: '',
        original_date: '',
        original_period: '',
        new_date: '',
        new_period: ''
      };
      await loadMakeupRequests(); // 申請一覧を更新
    } catch (err) {
      console.error('補講申請エラー:', err);
      error = err.response?.data?.error || '申請の送信に失敗しました。';
    } finally {
      loading = false;
    }
  }
</script>

<div class="card">
  <h2>補講申請</h2>

  {#if success}
    <p class="success">{success}</p>
  {/if}
  {#if error}
    <p class="error">{error}</p>
  {/if}

  <form on:submit|preventDefault={handleSubmit}>
    <div class="form-group">
      <label for="name">名前</label>
      <input id="name" type="text" bind:value={formData.name} placeholder="氏名を入力" required />
    </div>
    <div class="form-group">
      <label for="subject">科目</label>
      <input id="subject" type="text" bind:value={formData.subject} placeholder="科目名を入力" required />
    </div>

    <fieldset>
      <legend>変更前の日時</legend>
      <div class="form-group">
        <label for="original_date">日付</label>
        <select id="original_date" bind:value={formData.original_date} required>
          <option value="">日付を選択</option>
          {#each dates as date}
            <option value={date}>{date}</option>
          {/each}
        </select>
      </div>
      <div class="form-group">
        <label for="original_period">時限</label>
        <select id="original_period" bind:value={formData.original_period} required>
          <option value="">時限を選択</option>
          {#each periods as period}
            <option value={period}>{period}</option>
          {/each}
        </select>
      </div>
    </fieldset>

    <fieldset>
      <legend>変更後の日時</legend>
      <div class="form-group">
        <label for="new_date">日付</label>
        <select id="new_date" bind:value={formData.new_date} required>
          <option value="">日付を選択</option>
          {#each dates as date}
            <option value={date}>{date}</option>
          {/each}
        </select>
      </div>
      <div class="form-group">
        <label for="new_period">時限</label>
        <select id="new_period" bind:value={formData.new_period} required>
          <option value="">時限を選択</option>
          {#each periods as period}
            <option value={period}>{period}</option>
          {/each}
        </select>
      </div>
    </fieldset>

    <div class="button-group">
      <button type="submit" disabled={loading}>
        {loading ? '送信中...' : '申請する'}
      </button>
      <button type="button" on:click={() => showRequests = !showRequests} class="show-requests-btn">
        {showRequests ? '申請一覧を非表示' : '申請一覧を表示'}
      </button>
    </div>
  </form>
</div>

{#if showRequests}
  <div class="card">
    <h3>補講申請一覧</h3>
    {#if makeupRequests.length > 0}
      <table class="requests-table">
        <thead>
          <tr>
            <th>申請日時</th>
            <th>名前</th>
            <th>科目</th>
            <th>変更前</th>
            <th>変更後</th>
          </tr>
        </thead>
        <tbody>
          {#each makeupRequests as request}
            <tr>
              <td>{new Date(request.created_at).toLocaleString('ja-JP')}</td>
              <td>{request.name}</td>
              <td>{request.subject}</td>
              <td>{request.original_date} {request.original_period}</td>
              <td>{request.new_date} {request.new_period}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    {:else}
      <p>補講申請はありません</p>
    {/if}
  </div>
{/if}

<style>
  fieldset {
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 1rem;
    margin-bottom: 1.5rem;
  }
  
  legend {
    padding: 0 0.5rem;
    font-weight: 500;
    color: #333;
  }

  .button-group {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
  }

  .show-requests-btn {
    background-color: #17a2b8;
  }

  .show-requests-btn:hover {
    background-color: #138496;
  }

  .requests-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
  }

  .requests-table th,
  .requests-table td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid #ddd;
  }

  .requests-table th {
    background-color: #f8f9fa;
    font-weight: 600;
  }

  .requests-table tbody tr:nth-child(even) {
    background-color: #f8f9fa;
  }

  .requests-table tbody tr:hover {
    background-color: #e3f2fd;
  }
</style>