<script>
  import { createEventDispatcher, onMount } from 'svelte';
  
  const dispatch = createEventDispatcher();
  
  export let user;
  export let token;
  
  let qrCode = '';
  let qrData = '';
  let selectedDate = new Date().toISOString().split('T')[0];
  let attendances = [];
  let message = '';
  let error = '';

  onMount(() => {
    loadAttendance();
  });

  async function generateQR() {
    error = '';
    message = '';
    
    try {
      console.log('Generating QR with date:', selectedDate);
      console.log('Token exists:', !!token);
      console.log('Token length:', token ? token.length : 0);
      
      const requestBody = { date: selectedDate };
      console.log('Request body:', requestBody);
      
      const response = await fetch('http://localhost:5000/api/generate-qr', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(requestBody),
      });

      console.log('Response status:', response.status);

      const data = await response.json();
      console.log('Response data:', data);

      if (response.ok) {
        qrCode = data.qr_code;
        qrData = data.data;
        message = 'QR code generated successfully';
      } else if (response.status === 401) {
        error = 'セッションが期限切れです。再ログインしてください。';
        setTimeout(() => {
          logout();
        }, 2000);
      } else {
        error = data.error || `QR generation failed (${response.status})`;
        if (data.details) {
          error += `: ${data.details}`;
        }
      }
    } catch (err) {
      console.error('QR generation error:', err);
      error = `Connection failed: ${err.message}`;
    }
  }

  async function checkIn() {
    error = '';
    message = '';
    
    try {
      const response = await fetch('http://localhost:5000/api/check-in', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();

      if (response.ok) {
        message = data.message;
        loadAttendance();
      } else if (response.status === 401) {
        error = 'セッションが期限切れです。再ログインしてください。';
        setTimeout(() => {
          logout();
        }, 2000);
      } else {
        error = data.error || `Check-in failed (${response.status})`;
      }
    } catch (err) {
      console.error('Check-in error:', err);
      error = `Connection failed: ${err.message}`;
    }
  }

  async function checkOut() {
    error = '';
    message = '';
    
    try {
      const response = await fetch('http://localhost:5000/api/check-out', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();

      if (response.ok) {
        message = data.message;
        loadAttendance();
      } else if (response.status === 401) {
        error = 'セッションが期限切れです。再ログインしてください。';
        setTimeout(() => {
          logout();
        }, 2000);
      } else {
        error = data.error || `Check-out failed (${response.status})`;
      }
    } catch (err) {
      console.error('Check-out error:', err);
      error = `Connection failed: ${err.message}`;
    }
  }

  async function loadAttendance() {
    try {
      const response = await fetch('http://localhost:5000/api/attendance', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        attendances = await response.json();
      } else if (response.status === 401) {
        console.log('Token expired, logging out...');
        logout();
      } else {
        console.error('Failed to load attendance:', response.status);
      }
    } catch (err) {
      console.error('Failed to load attendance:', err);
    }
  }

  function logout() {
    dispatch('logout');
  }
</script>

<div>
  <h2>ダッシュボード</h2>
  <p>ようこそ、{user.username}さん</p>
  
  <button on:click={logout}>ログアウト</button>
  
  {#if message}
    <div style="color: green; margin: 10px 0;">{message}</div>
  {/if}
  
  {#if error}
    <div style="color: red; margin: 10px 0;">{error}</div>
  {/if}

  <h3>QRコード生成</h3>
  <div>
    <label for="date">日付:</label>
    <input
      id="date"
      type="date"
      bind:value={selectedDate}
    />
    <button on:click={generateQR}>QRコード生成</button>
  </div>
  
  {#if qrCode}
    <div>
      <h4>生成されたQRコード</h4>
      <img src={qrCode} alt="QR Code" />
      <p>データ: {qrData}</p>
    </div>
  {/if}

  <h3>勤怠管理</h3>
  <div>
    <button on:click={checkIn}>出勤</button>
    <button on:click={checkOut}>退勤</button>
  </div>

  <h3>勤怠履歴</h3>
  {#if attendances.length > 0}
    <table border="1">
      <thead>
        <tr>
          <th>日付</th>
          <th>出勤時刻</th>
          <th>退勤時刻</th>
        </tr>
      </thead>
      <tbody>
        {#each attendances as attendance}
          <tr>
            <td>{attendance.date}</td>
            <td>{attendance.check_in ? new Date(attendance.check_in).toLocaleString() : '-'}</td>
            <td>{attendance.check_out ? new Date(attendance.check_out).toLocaleString() : '-'}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  {:else}
    <p>勤怠履歴がありません</p>
  {/if}
</div>