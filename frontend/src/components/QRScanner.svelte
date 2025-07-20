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

  function formatDateTime(dateTime) {
    if (!dateTime) return '-';
    return new Date(dateTime).toLocaleString('ja-JP');
  }

  function formatDate(dateStr) {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('ja-JP');
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
      <label for="qr-input">QRデータ入力</label>
      <input 
        id="qr-input"
        type="text" 
        bind:value={manualInput}
        placeholder="QRデータを入力 (例: 山田太郎|2025-01-15)"
        disabled={loading}
      />
      <small class="input-help">
        QRコードから読み取った文字列を入力してください。形式：「ユーザー名|日付」
      </small>
    </div>
    <div class="button-group">
      <button on:click={manualCheck} disabled={loading || !manualInput.trim()} class="punch-btn">
        {loading ? '打刻中...' : '打刻'}
      </button>
      <button on:click={reset} disabled={loading} class="reset-btn">
        リセット
      </button>
    </div>
  </div>
  
  {#if attendanceResult}
    <div class="attendance-result">
      <h3>打刻結果</h3>
      <div class="result-card">
        <div class="result-header">
          <h4>打刻情報</h4>
          <span class="status-badge">出勤記録</span>
        </div>
        
        <table class="result-table">
          <tr>
            <th>ユーザーID</th>
            <td>{attendanceResult.user_id}</td>
          </tr>
          <tr>
            <th>対象日付</th>
            <td class="date-cell">{formatDate(attendanceResult.date)}</td>
          </tr>
          <tr class="time-row">
            <th>打刻時刻</th>
            <td class="time-cell recorded">
              {formatDateTime(attendanceResult.check_in)}
            </td>
          </tr>
        </table>
        
        <div class="next-action">
          <p>打刻が完了しました</p>
          <p>本日の出勤が記録されました</p>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .manual-input-section {
    margin-bottom: 2rem;
  }
  
  .input-help {
    display: block;
    margin-top: 0.25rem;
    font-size: 0.875em;
    color: #6c757d;
    font-style: italic;
  }
  
  .button-group {
    display: flex;
    gap: 1rem;
    margin-top: 1rem;
  }

  .punch-btn {
    background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
    border: none;
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 6px;
    cursor: pointer;
    font-size: 1em;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 2px 4px rgba(0, 123, 255, 0.3);
  }

  .punch-btn:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 123, 255, 0.4);
  }

  .punch-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }

  .reset-btn {
    background: #6c757d;
    border: none;
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 6px;
    cursor: pointer;
    font-size: 1em;
    transition: all 0.3s ease;
  }

  .reset-btn:hover:not(:disabled) {
    background: #5a6268;
    transform: translateY(-1px);
  }
  
  .attendance-result {
    margin-top: 2rem;
  }

  .result-card {
    border-radius: 8px;
    background: white;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    border: 2px solid #28a745;
  }

  .result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    background: #f8f9fa;
    border-bottom: 1px solid #e9ecef;
  }

  .result-header h4 {
    margin: 0;
    color: #495057;
  }

  .status-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.875em;
    font-weight: 600;
    color: white;
    background: #28a745;
  }
  
  .result-table {
    margin: 0;
    width: 100%;
    border-collapse: collapse;
  }

  .result-table th,
  .result-table td {
    padding: 0.75rem 1.5rem;
    text-align: left;
    border-bottom: 1px solid #e9ecef;
  }

  .result-table th {
    background: #f8f9fa;
    font-weight: 600;
    color: #495057;
    width: 30%;
  }

  .result-table td {
    color: #6c757d;
  }

  .date-cell {
    font-weight: 600;
    color: #495057;
    font-size: 1.1em;
  }

  .time-cell {
    font-family: monospace;
    font-size: 0.95em;
  }

  .time-cell.recorded {
    color: #28a745;
    font-weight: 600;
  }

  .next-action {
    padding: 1rem 1.5rem;
    background: #f8f9fa;
    border-top: 1px solid #e9ecef;
  }

  .next-action p {
    margin: 0.5rem 0;
    color: #495057;
  }

  .next-action p:first-child {
    font-weight: 600;
    color: #28a745;
  }

  .error {
    background: #f8d7da;
    color: #721c24;
    padding: 0.75rem 1rem;
    border-radius: 6px;
    border: 1px solid #f5c6cb;
    margin: 0.5rem 0;
  }

  .success {
    background: #d4edda;
    color: #155724;
    padding: 0.75rem 1rem;
    border-radius: 6px;
    border: 1px solid #c3e6cb;
    margin: 0.5rem 0;
  }

  @media (max-width: 768px) {
    .button-group {
      flex-direction: column;
    }
    
    .result-table th,
    .result-table td {
      padding: 0.5rem;
      font-size: 0.9em;
    }
    
    .result-header {
      padding: 0.75rem 1rem;
      flex-direction: column;
      gap: 0.5rem;
      text-align: center;
    }
  }
</style>