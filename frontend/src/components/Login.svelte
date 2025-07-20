<script>
  import { createEventDispatcher } from 'svelte';
  import { authAPI } from '../lib/api.js';

  const dispatch = createEventDispatcher();

  let password = '';
  let error = '';
  let loading = false;

  async function handleLogin() {
    if (!password) {
      error = 'パスワードを入力してください';
      return;
    }

    error = '';
    loading = true;

    try {
      await authAPI.login(password); 
      dispatch('login-success');
      password = '';
    } catch (err) {
      error = err.response?.data?.error || 'ログインに失敗しました';
    } finally {
      loading = false;
    }
  }

  function handleKeydown(event) {
    if (event.key === 'Enter') {
      handleLogin();
    }
  }
</script>

<div class="login-modal">
  <div class="login-content">
    <h3>管理者ログイン</h3>
    
    {#if error}
      <p class="error">{error}</p>
    {/if}
    
    <div class="form-group">
      <label for="password">パスワード</label>
      <input 
        id="password"
        type="password" 
        bind:value={password}
        on:keydown={handleKeydown}
        placeholder="パスワードを入力"
        disabled={loading}
        autofocus
      />
    </div>
    
    <div class="button-group">
      <button on:click={handleLogin} disabled={loading || !password}>
        {loading ? 'ログイン中...' : 'ログイン'}
      </button>
      <button on:click={() => dispatch('cancel')} disabled={loading}>
        キャンセル
      </button>
    </div>
  </div>
</div>

<style>
  .login-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }

  .login-content {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    min-width: 300px;
    max-width: 400px;
  }

  .button-group {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
  }

  .button-group button {
    padding: 0.5rem 1rem;
  }

  h3 {
    margin-top: 0;
    text-align: center;
    color: #333;
  }
</style>
