<script>
  import { onMount } from 'svelte';
  import { userAPI } from '../lib/api.js';

  let users = [];
  let newUser = { name: '', email: '' };
  let error = '';
  let success = '';
  let loading = false;

  onMount(() => {
    loadUsers();
  });

  async function loadUsers() {
    try {
      error = '';
      const response = await userAPI.getAll();
      users = response.data;
    } catch (err) {
      console.error('Load users error:', err);
      error = 'ユーザーの読み込みに失敗しました';
    }
  }

  async function createUser() {
    error = '';
    success = '';
    
    // フロントエンド側での入力検証
    if (!newUser.name || !newUser.name.trim()) {
      error = '名前を入力してください';
      return;
    }

    if (!newUser.email || !newUser.email.trim()) {
      error = 'メールアドレスを入力してください';
      return;
    }

    // 簡単なメール形式チェック
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(newUser.email.trim())) {
      error = '正しいメールアドレスの形式で入力してください';
      return;
    }

    loading = true;
    
    try {
      // APIコール時にトリムした値を送信
      const userData = {
        name: newUser.name.trim(),
        email: newUser.email.trim()
      };
      
      console.log('Creating user:', userData); // デバッグ用
      
      const response = await userAPI.create(userData);
      console.log('User created:', response.data); // デバッグ用
      
      success = 'ユーザーを作成しました';
      newUser = { name: '', email: '' };
      await loadUsers();
      
    } catch (err) {
      console.error('Create user error:', err);
      
      // エラーレスポンスの詳細を表示
      if (err.response && err.response.data && err.response.data.error) {
        error = err.response.data.error;
      } else if (err.response && err.response.status) {
        error = `ユーザーの作成に失敗しました (HTTP ${err.response.status})`;
      } else {
        error = 'ユーザーの作成に失敗しました';
      }
    } finally {
      loading = false;
    }
  }

  async function deleteUser(id) {
    if (!confirm('このユーザーを削除しますか？')) return;
    
    try {
      error = '';
      success = '';
      await userAPI.delete(id);
      success = 'ユーザーを削除しました';
      await loadUsers();
    } catch (err) {
      console.error('Delete user error:', err);
      error = 'ユーザーの削除に失敗しました';
    }
  }
</script>

<div class="card">
  <h2>新規ユーザー登録</h2>
  
  {#if error}
    <p class="error">{error}</p>
  {/if}
  
  {#if success}
    <p class="success">{success}</p>
  {/if}
  
  <form on:submit|preventDefault={createUser}>
    <div class="form-group">
      <label for="name">名前</label>
      <input 
        id="name"
        type="text" 
        bind:value={newUser.name} 
        placeholder="山田太郎"
        disabled={loading}
        required
      />
    </div>
    
    <div class="form-group">
      <label for="email">メールアドレス</label>
      <input 
        id="email"
        type="email" 
        bind:value={newUser.email} 
        placeholder="yamada@example.com"
        disabled={loading}
        required
      />
    </div>
    
    <button type="submit" disabled={loading}>
      {loading ? '作成中...' : 'ユーザー登録'}
    </button>
  </form>
</div>

<div class="card">
  <h2>登録ユーザー一覧</h2>
  
  {#if users.length === 0}
    <p>登録されているユーザーはいません</p>
  {:else}
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>名前</th>
          <th>メールアドレス</th>
          <th>作成日</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        {#each users as user}
          <tr>
            <td>{user.id}</td>
            <td>{user.name}</td>
            <td>{user.email}</td>
            <td>{user.created_at ? new Date(user.created_at).toLocaleDateString('ja-JP') : '-'}</td>
            <td>
              <button on:click={() => deleteUser(user.id)}>削除</button>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
</div>