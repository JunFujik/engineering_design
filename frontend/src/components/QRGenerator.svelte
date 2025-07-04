<script>
  import { onMount } from 'svelte';
  import { userAPI, qrAPI } from '../lib/api.js';

  let users = [];
  let selectedUserId = '';
  let selectedDate = new Date().toISOString().split('T')[0];
  let qrCode = '';
  let qrData = '';
  let error = '';
  let success = '';
  let loading = false;

  onMount(() => {
    loadUsers();
  });

  async function loadUsers() {
    try {
      const response = await userAPI.getAll();
      users = response.data;
    } catch (err) {
      error = 'ユーザーの読み込みに失敗しました';
    }
  }

  async function generateQR() {
    error = '';
    success = '';
    
    if (!selectedUserId) {
      error = 'ユーザーを選択してください';
      return;
    }

    loading = true;
    try {
      const response = await qrAPI.generate({
        user_id: parseInt(selectedUserId),
        date: selectedDate
      });
      qrCode = response.data.qr_code;
      qrData = response.data.qr_data;
      success = 'QRコードを生成しました';
    } catch (err) {
      error = 'QRコードの生成に失敗しました';
    } finally {
      loading = false;
    }
  }

  async function sendEmail() {
    error = '';
    success = '';
    
    if (!selectedUserId) {
      error = 'ユーザーを選択してください';
      return;
    }

    loading = true;
    try {
      await qrAPI.sendEmail({
        user_id: parseInt(selectedUserId),
        date: selectedDate
      });
      success = 'QRコードをメールで送信しました';
    } catch (err) {
      error = err.response?.data?.error || 'メールの送信に失敗しました';
    } finally {
      loading = false;
    }
  }
</script>

<div class="card">
  <h2>QRコード生成</h2>
  
  {#if error}
    <p class="error">{error}</p>
  {/if}
  
  {#if success}
    <p class="success">{success}</p>
  {/if}
  
  <div class="form-group">
    <label for="user">ユーザー選択</label>
    <select id="user" bind:value={selectedUserId}>
      <option value="">ユーザーを選択してください</option>
      {#each users as user}
        <option value={user.id}>{user.name} ({user.email})</option>
      {/each}
    </select>
  </div>
  
  <div class="form-group">
    <label for="date">日付</label>
    <input 
      id="date"
      type="date" 
      bind:value={selectedDate}
    />
  </div>
  
  <div style="display: flex; gap: 1rem;">
    <button on:click={generateQR} disabled={loading}>
      {loading ? '生成中...' : 'QRコード生成'}
    </button>
    <button on:click={sendEmail} disabled={loading}>
      {loading ? '送信中...' : 'メールで送信'}
    </button>
  </div>
  
  {#if qrCode}
    <div class="qr-code">
      <h3>生成されたQRコード</h3>
      <img src={qrCode} alt="QR Code" />
      <p>QRデータ: {qrData}</p>
    </div>
  {/if}
</div>

<style>
  .qr-code {
    margin-top: 2rem;
  }
</style>