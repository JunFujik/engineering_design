<script>
  import { createEventDispatcher } from 'svelte';
  
  const dispatch = createEventDispatcher();
  
  let username = '';
  let password = '';
  let error = '';
  let loading = false;

  async function handleLogin() {
    if (!username || !password) {
      error = 'ユーザー名とパスワードを入力してください';
      return;
    }

    loading = true;
    error = '';

    try {
      console.log('Attempting login with username:', username);
      
      const response = await fetch('http://localhost:5000/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      console.log('Login response status:', response.status);
      const data = await response.json();
      console.log('Login response data:', data);

      if (response.ok) {
        console.log('Login successful, dispatching event');
        dispatch('login', {
          token: data.access_token,
          user: data.user
        });
      } else {
        error = data.error || 'ログインに失敗しました';
      }
    } catch (err) {
      console.error('Login error:', err);
      error = 'サーバーへの接続に失敗しました';
    } finally {
      loading = false;
    }
  }

  function showRegister() {
    dispatch('showRegister');
  }

  function handleKeyPress(event) {
    if (event.key === 'Enter') {
      handleLogin();
    }
  }
</script>

<div class="login-container">
  <h2>ログイン</h2>
  
  {#if error}
    <div class="error">{error}</div>
  {/if}

  <form on:submit|preventDefault={handleLogin}>
    <div class="form-group">
      <label for="username">ユーザー名:</label>
      <input
        id="username"
        type="text"
        bind:value={username}
        disabled={loading}
        on:keypress={handleKeyPress}
        placeholder="ユーザー名を入力"
      />
    </div>

    <div class="form-group">
      <label for="password">パスワード:</label>
      <input
        id="password"
        type="password"
        bind:value={password}
        disabled={loading}
        on:keypress={handleKeyPress}
        placeholder="パスワードを入力"
      />
    </div>

    <button type="submit" disabled={loading}>
      {loading ? 'ログイン中...' : 'ログイン'}
    </button>
  </form>

  <p class="register-link">
    アカウントをお持ちでない方は
    <button class="link-button" on:click={showRegister}>新規登録</button>
  </p>
</div>

<style>
  .login-container {
    max-width: 400px;
    margin: 0 auto;
    padding: 20px;
  }

  .form-group {
    margin-bottom: 15px;
  }

  label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
  }

  input {
    width: 100%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 16px;
  }

  button {
    width: 100%;
    padding: 10px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
  }

  button:hover:not(:disabled) {
    background-color: #0056b3;
  }

  button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }

  .error {
    background-color: #f8d7da;
    color: #721c24;
    padding: 10px;
    border-radius: 4px;
    margin-bottom: 15px;
  }

  .register-link {
    text-align: center;
    margin-top: 20px;
  }

  .link-button {
    background: none;
    color: #007bff;
    border: none;
    cursor: pointer;
    text-decoration: underline;
    width: auto;
    padding: 0;
  }

  .link-button:hover {
    color: #0056b3;
  }
</style>