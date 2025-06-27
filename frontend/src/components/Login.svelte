<script>
  import { createEventDispatcher } from 'svelte';
  
  const dispatch = createEventDispatcher();
  
  let username = '';
  let password = '';
  let error = '';
  let loading = false;

  async function handleLogin() {
    if (!username || !password) {
      error = 'Username and password are required';
      return;
    }

    loading = true;
    error = '';

    try {
      const response = await fetch('http://localhost:5000/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (response.ok) {
        dispatch('login', {
          token: data.access_token,
          user: data.user
        });
      } else {
        error = data.error || 'Login failed';
      }
    } catch (err) {
      error = 'Connection failed';
    } finally {
      loading = false;
    }
  }

  function showRegister() {
    dispatch('showRegister');
  }
</script>

<div>
  <h2>ログイン</h2>
  
  {#if error}
    <div>{error}</div>
  {/if}

  <form on:submit|preventDefault={handleLogin}>
    <div>
      <label for="username">ユーザー名:</label>
      <input
        id="username"
        type="text"
        bind:value={username}
        disabled={loading}
      />
    </div>

    <div>
      <label for="password">パスワード:</label>
      <input
        id="password"
        type="password"
        bind:value={password}
        disabled={loading}
      />
    </div>

    <button type="submit" disabled={loading}>
      {loading ? 'ログイン中...' : 'ログイン'}
    </button>
  </form>

  <p>
    <button on:click={showRegister}>新規登録</button>
  </p>
</div>