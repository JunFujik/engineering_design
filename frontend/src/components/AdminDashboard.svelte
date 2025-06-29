<script>
  import { createEventDispatcher, onMount } from 'svelte';
  
  const dispatch = createEventDispatcher();
  
  export let user;
  export let token;
  
  let users = [];
  let attendances = [];
  let selectedUserId = '';
  let message = '';
  let error = '';
  let activeTab = 'users';
  
  // 新規勤怠記録追加用
  let newAttendance = {
    user_id: '',
    date: new Date().toISOString().split('T')[0],
    check_in: '',
    check_out: '',
    is_present: true,
    class_count: 0
  };

  onMount(() => {
    loadUsers();
    loadAllAttendance();
  });

  async function loadUsers() {
    try {
      const response = await fetch('http://localhost:5000/api/admin/users', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        users = await response.json();
      } else if (response.status === 403) {
        error = '管理者権限が必要です';
      } else if (response.status === 401) {
        logout();
      } else {
        error = 'ユーザー一覧の取得に失敗しました';
      }
    } catch (err) {
      console.error('Failed to load users:', err);
      error = 'サーバーへの接続に失敗しました';
    }
  }

  async function loadAllAttendance() {
    try {
      let url = 'http://localhost:5000/api/admin/attendance';
      if (selectedUserId) {
        url += `?user_id=${selectedUserId}`;
      }
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        attendances = await response.json();
      } else if (response.status === 403) {
        error = '管理者権限が必要です';
      } else if (response.status === 401) {
        logout();
      } else {
        error = '勤怠データの取得に失敗しました';
      }
    } catch (err) {
      console.error('Failed to load attendance:', err);
      error = 'サーバーへの接続に失敗しました';
    }
  }

  async function addAttendance() {
    if (!newAttendance.user_id || !newAttendance.date) {
      error = 'ユーザーと日付は必須です';
      return;
    }

    try {
      const requestData = {
        user_id: parseInt(newAttendance.user_id),
        date: newAttendance.date,
        is_present: newAttendance.is_present,
        class_count: parseInt(newAttendance.class_count) || 0
      };

      // 時刻が入力されている場合は追加
      if (newAttendance.check_in) {
        requestData.check_in = `${newAttendance.date}T${newAttendance.check_in}:00`;
      }
      if (newAttendance.check_out) {
        requestData.check_out = `${newAttendance.date}T${newAttendance.check_out}:00`;
      }

      const response = await fetch('http://localhost:5000/api/admin/attendance', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(requestData)
      });

      const data = await response.json();

      if (response.ok) {
        message = '勤怠記録を保存しました';
        // フォームをリセット
        newAttendance = {
          user_id: '',
          date: new Date().toISOString().split('T')[0],
          check_in: '',
          check_out: '',
          is_present: true,
          class_count: 0
        };
        loadAllAttendance();
      } else if (response.status === 403) {
        error = '管理者権限が必要です';
      } else if (response.status === 401) {
        logout();
      } else {
        error = data.error || '勤怠記録の保存に失敗しました';
      }
    } catch (err) {
      console.error('Failed to add attendance:', err);
      error = 'サーバーへの接続に失敗しました';
    }
  }

  async function deleteAttendance(attendanceId) {
    if (!confirm('この勤怠記録を削除しますか？')) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:5000/api/admin/attendance/${attendanceId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();

      if (response.ok) {
        message = '勤怠記録を削除しました';
        loadAllAttendance();
      } else if (response.status === 403) {
        error = '管理者権限が必要です';
      } else if (response.status === 401) {
        logout();
      } else {
        error = data.error || '勤怠記録の削除に失敗しました';
      }
    } catch (err) {
      console.error('Failed to delete attendance:', err);
      error = 'サーバーへの接続に失敗しました';
    }
  }

  function filterByUser() {
    loadAllAttendance();
  }

  function clearMessages() {
    message = '';
    error = '';
  }

  function logout() {
    dispatch('logout');
  }
</script>

<div>
  <h2>管理者ダッシュボード</h2>
  <p>ようこそ、{user.username}さん（管理者）</p>
  
  <button on:click={logout}>ログアウト</button>
  
  {#if message}
    <div style="color: green; margin: 10px 0; padding: 10px; background-color: #d4edda; border-radius: 4px;">
      {message}
      <button style="float: right; background: none; border: none; color: green; cursor: pointer;" on:click={clearMessages}>×</button>
    </div>
  {/if}
  
  {#if error}
    <div style="color: red; margin: 10px 0; padding: 10px; background-color: #f8d7da; border-radius: 4px;">
      {error}
      <button style="float: right; background: none; border: none; color: red; cursor: pointer;" on:click={clearMessages}>×</button>
    </div>
  {/if}

  <!-- タブ切り替え -->
  <div style="margin: 20px 0;">
    <button 
      class:active={activeTab === 'users'} 
      on:click={() => activeTab = 'users'}
      style="margin-right: 10px; padding: 10px 20px; border: 1px solid #ccc; background: {activeTab === 'users' ? '#007bff' : 'white'}; color: {activeTab === 'users' ? 'white' : 'black'};"
    >
      ユーザー管理
    </button>
    <button 
      class:active={activeTab === 'attendance'} 
      on:click={() => activeTab = 'attendance'}
      style="margin-right: 10px; padding: 10px 20px; border: 1px solid #ccc; background: {activeTab === 'attendance' ? '#007bff' : 'white'}; color: {activeTab === 'attendance' ? 'white' : 'black'};"
    >
      勤怠管理
    </button>
    <button 
      class:active={activeTab === 'add'} 
      on:click={() => activeTab = 'add'}
      style="padding: 10px 20px; border: 1px solid #ccc; background: {activeTab === 'add' ? '#007bff' : 'white'}; color: {activeTab === 'add' ? 'white' : 'black'};"
    >
      勤怠追加
    </button>
  </div>

  {#if activeTab === 'users'}
    <h3>ユーザー一覧</h3>
    {#if users.length > 0}
      <table border="1" style="width: 100%; border-collapse: collapse;">
        <thead>
          <tr style="background-color: #f8f9fa;">
            <th style="padding: 10px;">ID</th>
            <th style="padding: 10px;">ユーザー名</th>
            <th style="padding: 10px;">メールアドレス</th>
            <th style="padding: 10px;">管理者</th>
            <th style="padding: 10px;">登録日</th>
          </tr>
        </thead>
        <tbody>
          {#each users as user}
            <tr>
              <td style="padding: 10px;">{user.id}</td>
              <td style="padding: 10px;">{user.username}</td>
              <td style="padding: 10px;">{user.email}</td>
              <td style="padding: 10px;">{user.is_admin ? '✓' : '-'}</td>
              <td style="padding: 10px;">{new Date(user.created_at).toLocaleDateString()}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    {:else}
      <p>ユーザーが見つかりません</p>
    {/if}
  {/if}

  {#if activeTab === 'attendance'}
    <h3>勤怠履歴管理</h3>
    
    <div style="margin-bottom: 20px;">
      <label for="userFilter">ユーザーでフィルター:</label>
      <select id="userFilter" bind:value={selectedUserId} on:change={filterByUser} style="margin-left: 10px; padding: 5px;">
        <option value="">全ユーザー</option>
        {#each users as user}
          <option value={user.id}>{user.username}</option>
        {/each}
      </select>
    </div>

    {#if attendances.length > 0}
      <table border="1" style="width: 100%; border-collapse: collapse;">
        <thead>
          <tr style="background-color: #f8f9fa;">
            <th style="padding: 10px;">ユーザー</th>
            <th style="padding: 10px;">日付</th>
            <th style="padding: 10px;">出勤時刻</th>
            <th style="padding: 10px;">退勤時刻</th>
            <th style="padding: 10px;">出席</th>
            <th style="padding: 10px;">授業数</th>
            <th style="padding: 10px;">操作</th>
          </tr>
        </thead>
        <tbody>
          {#each attendances as attendance}
            <tr>
              <td style="padding: 10px;">{attendance.username}</td>
              <td style="padding: 10px;">{attendance.date}</td>
              <td style="padding: 10px;">{attendance.check_in ? new Date(attendance.check_in).toLocaleString() : '-'}</td>
              <td style="padding: 10px;">{attendance.check_out ? new Date(attendance.check_out).toLocaleString() : '-'}</td>
              <td style="padding: 10px;">{attendance.is_present ? '出席' : '欠席'}</td>
              <td style="padding: 10px;">{attendance.class_count}</td>
              <td style="padding: 10px;">
                <button 
                  on:click={() => deleteAttendance(attendance.id)}
                  style="background-color: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer;"
                >
                  削除
                </button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    {:else}
      <p>勤怠履歴がありません</p>
    {/if}
  {/if}

  {#if activeTab === 'add'}
    <h3>勤怠記録追加</h3>
    
    <form on:submit|preventDefault={addAttendance} style="max-width: 500px;">
      <div style="margin-bottom: 15px;">
        <label for="selectUser">ユーザー:</label><br>
        <select id="selectUser" bind:value={newAttendance.user_id} required style="width: 100%; padding: 8px; margin-top: 5px;">
          <option value="">ユーザーを選択</option>
          {#each users as user}
            <option value={user.id}>{user.username}</option>
          {/each}
        </select>
      </div>

      <div style="margin-bottom: 15px;">
        <label for="attendanceDate">日付:</label><br>
        <input 
          id="attendanceDate" 
          type="date" 
          bind:value={newAttendance.date} 
          required 
          style="width: 100%; padding: 8px; margin-top: 5px;"
        />
      </div>

      <div style="margin-bottom: 15px;">
        <label for="checkInTime">出勤時刻:</label><br>
        <input 
          id="checkInTime" 
          type="time" 
          bind:value={newAttendance.check_in} 
          style="width: 100%; padding: 8px; margin-top: 5px;"
        />
      </div>

      <div style="margin-bottom: 15px;">
        <label for="checkOutTime">退勤時刻:</label><br>
        <input 
          id="checkOutTime" 
          type="time" 
          bind:value={newAttendance.check_out} 
          style="width: 100%; padding: 8px; margin-top: 5px;"
        />
      </div>

      <div style="margin-bottom: 15px;">
        <label>
          <input 
            type="checkbox" 
            bind:checked={newAttendance.is_present}
            style="margin-right: 8px;"
          />
          出席
        </label>
      </div>

      <div style="margin-bottom: 20px;">
        <label for="classCount">授業数:</label><br>
        <input 
          id="classCount" 
          type="number" 
          min="0" 
          bind:value={newAttendance.class_count} 
          style="width: 100%; padding: 8px; margin-top: 5px;"
        />
      </div>

      <button 
        type="submit" 
        style="width: 100%; padding: 12px; background-color: #28a745; color: white; border: none; border-radius: 4px; font-size: 16px; cursor: pointer;"
      >
        勤怠記録を追加
      </button>
    </form>
  {/if}
</div>