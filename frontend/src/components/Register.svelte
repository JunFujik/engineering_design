<script>
  import { createEventDispatcher } from 'svelte';
  
  const dispatch = createEventDispatcher();
  
  let username = '';
  let email = '';
  let password = '';
  let confirmPassword = '';
  let error = '';
  let success = '';
  let loading = false;

  async function handleRegister() {
    if (!username || !email || !password || !confirmPassword) {
      error = 'All fields are required';
      return;
    }

    if (password !== confirmPassword) {
      error = 'Passwords do not match';
      return;
    }

    loading = true;
    error = '';
    success = '';

    try {
      const response = await fetch('http://localhost:5000/api/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        success = 'Registration successful! Please login.';
        username = '';
        email = '';
        password = '';
        confirmPassword = '';
        setTimeout(() => {
          showLogin();
        }, 2000);
      } else {
        error = data.error || 'Registration failed';
      }
    } catch (err) {
      error = 'Connection failed';
    } finally {
      loading = false;
    }
  }

  function showLogin() {
    dispatch('showLogin');
  }
</script>

<div>
  <h2>新規登録</h2>
  
  {#if error}
    <div>{error}</div>
  {/if}

  {#if success}
    <div>{success}</div>
  {/if}

  <form on:submit|preventDefault={handleRegister}>
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
      <label for="email">メールアドレス:</label>
      <input
        id="email"
        type="email"
        bind:value={email}
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

    <div>
      <label for="confirmPassword">パスワード確認:</label>
      <input
        id="confirmPassword"
        type="password"
        bind:value={confirmPassword}
        disabled={loading}
      />
    </div>

    <button type="submit" disabled={loading}>
      {loading ? '登録中...' : '登録'}
    </button>
  </form>

  <p>
    <button on:click={showLogin}>ログインに戻る</button>
  </p>
</div>