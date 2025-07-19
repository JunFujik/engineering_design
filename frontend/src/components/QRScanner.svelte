<script>
  import { attendanceAPI } from '../lib/api.js';

  let error = '';
  let success = '';
  let manualInput = '';
  let attendanceResult = null;
  let loading = false;

  async function checkAttendance(qrData) {
    error = '';
    success = '';
    attendanceResult = null;
    loading = true;

    try {
      const response = await attendanceAPI.check({
        qr_data: qrData
      });
      
      success = response.data.message;
      attendanceResult = response.data.attendance;
    } catch (err) {
      error = err.response?.data?.error || '打刻に失敗しました';
      if (err.response?.data?.attendance) {
        attendanceResult = err.response.data.attendance;
      }
    } finally {
      loading = false;
    }
  }

  async function manualCheck() {
    if (!manualInput || !manualInput.trim()) {
      error = 'QRデータを入力してください';
      return;
    }
    
    await checkAttendance(manualInput.trim());
  }

  function reset() {
    error = '';
    success = '';
    attendanceResult = null;
    manualInput = '';
  }
</script>

<div class="card">
  <h2>QRコード読取・打刻</h2>
  
  {#if error}
    <p class="error">{error}</p>
  {/if}
  
  {#if success}
    <p class="success">{success}</p>
  {/if}
  
  <div class="manual-input-section">
    <div class="form-group">
      <input 
        id="qr-input"
        type="text" 
        bind:value={manualInput}
        placeholder="QRデータを入力 (例: 山田太郎|2024-01-01)"
        disabled={loading}
      />
    </div>
    <div class="button-group">
      <button on:click={manualCheck} disabled={loading || !manualInput.trim()}>
        {loading ? '打刻中...' : '打刻'}
      </button>
      <button on:click={reset} disabled={loading}>
        リセット
      </button>
    </div>
  </div>
  
  {#if attendanceResult}
    <div class="attendance-result">
      <h3>打刻情報</h3>
      <table>
        <tr>
          <th>ユーザーID</th>
          <td>{attendanceResult.user_id}</td>
        </tr>
        <tr>
          <th>日付</th>
          <td>{attendanceResult.date}</td>
        </tr>
        <tr>
          <th>出勤時刻</th>
          <td>{attendanceResult.check_in ? new Date(attendanceResult.check_in).toLocaleString('ja-JP') : '-'}</td>
        </tr>
        <tr>
          <th>退勤時刻</th>
          <td>{attendanceResult.check_out ? new Date(attendanceResult.check_out).toLocaleString('ja-JP') : '-'}</td>
        </tr>
      </table>
    </div>
  {/if}
</div>

<style>
  .manual-input-section {
    margin-bottom: 2rem;
  }
  
  .button-group {
    display: flex;
    gap: 1rem;
  }
  
  .attendance-result {
    margin-top: 2rem;
    padding: 1rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    background-color: #f8f9fa;
  }
  
  .attendance-result table {
    margin: 1rem 0;
    width: 100%;
    max-width: 400px;
  }
  
  .attendance-result th {
    background-color: #e9ecef;
    width: 30%;
  }
</style>