<script>
  import { onMount, onDestroy } from 'svelte';
  import { Html5QrcodeScanner } from 'html5-qrcode';
  import { attendanceAPI } from '../lib/api.js';

  let scanner;
  let scanResult = '';
  let error = '';
  let success = '';
  let manualInput = '';
  let attendanceResult = null;

  onMount(() => {
    // Initialize QR scanner
    scanner = new Html5QrcodeScanner(
      "qr-reader",
      { 
        fps: 10, 
        qrbox: { width: 250, height: 250 },
        aspectRatio: 1.0
      }
    );
    
    scanner.render(onScanSuccess, onScanFailure);
  });

  onDestroy(() => {
    if (scanner) {
      scanner.clear();
    }
  });

  function onScanSuccess(decodedText) {
    scanResult = decodedText;
    checkAttendance(decodedText);
    if (scanner) {
      scanner.clear();
    }
  }

  function onScanFailure(error) {
    // Handle scan failure silently
  }

  async function checkAttendance(qrData) {
    error = '';
    success = '';
    attendanceResult = null;

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
    }
  }

  async function manualCheck() {
    if (!manualInput) {
      error = 'QRデータを入力してください';
      return;
    }
    
    scanResult = manualInput;
    await checkAttendance(manualInput);
  }

  function restartScanner() {
    scanResult = '';
    error = '';
    success = '';
    attendanceResult = null;
    manualInput = '';
    
    if (scanner) {
      scanner.render(onScanSuccess, onScanFailure);
    }
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
  
  {#if !scanResult}
    <div id="qr-reader"></div>
    
    <div style="margin-top: 2rem;">
      <h3>手動入力</h3>
      <div class="form-group">
        <input 
          type="text" 
          bind:value={manualInput}
          placeholder="QRデータを入力 (例: 山田太郎|2024-01-01)"
        />
      </div>
      <button on:click={manualCheck}>手動で打刻</button>
    </div>
  {:else}
    <div class="scan-result">
      <h3>スキャン結果</h3>
      <p><strong>QRデータ:</strong> {scanResult}</p>
      
      {#if attendanceResult}
        <h4>打刻情報</h4>
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
      {/if}
      
      <button on:click={restartScanner} style="margin-top: 1rem;">
        新しいQRコードをスキャン
      </button>
    </div>
  {/if}
</div>

<style>
  #qr-reader {
    width: 100%;
    max-width: 500px;
    margin: 0 auto;
  }
  
  .scan-result {
    text-align: center;
    padding: 2rem;
  }
  
  .scan-result table {
    margin: 1rem auto;
    max-width: 400px;
  }
</style>