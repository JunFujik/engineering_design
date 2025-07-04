<script>
  import { onMount } from 'svelte';
  import { userAPI } from '../lib/api.js';

  let users = [];
  let newUser = { name: '', email: '' };
  let error = '';
  let success = '';

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

  async function createUser() {
    error = '';
    success = '';
    
    if (!newUser.name || !newUser.email) {
      error = '名前とメールアドレスを入力してください';
      return;
    }

    try {
      await userAPI.create(newUser);
      success = 'ユーザーを作成しました';
      newUser = { name: '', email: '' };
      await loadUsers();
    } catch (err) {
      error = err.response?.data?.error || 'ユーザーの作成に失敗しました';
    }
  }

  async function deleteUser(id) {
    if (!confirm('このユーザーを削除しますか？')) return;
    
    try {
      await userAPI.delete(id);
      success = 'ユーザーを削除しました';
      await loadUsers();
    } catch (err) {
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
  
  <div class="form-group">
    <label for="name">名前</label>
    <input 
      id="name"
      type="text" 
      bind:value={newUser.name} 
      placeholder="山田太郎"
    />
  </div>
  
  <div class="form-group">
    <label for="email">メールアドレス</label>
    <input 
      id="email"
      type="email" 
      bind:value={newUser.email} 
      placeholder="yamada@example.com"
    />
  </div>
  
  <button on:click={createUser}>ユーザー登録</button>
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
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        {#each users as user}
          <tr>
            <td>{user.id}</td>
            <td>{user.name}</td>
            <td>{user.email}</td>
            <td>
              <button on:click={() => deleteUser(user.id)}>削除</button>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
</div>