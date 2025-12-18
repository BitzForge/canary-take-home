<template>
  <div class="page">
    <h1>Login</h1>
    <button @click="loginWithGoogle">Sign in with Google</button>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import axios from 'axios'
import { googleTokenLogin,  } from 'vue3-google-login'
import type { GoogleAuthResponse } from '../type'

const router = useRouter()

const loginWithGoogle = async () => {
  try {
    const authResult: GoogleAuthResponse = await googleTokenLogin()

    console.log(authResult)

    const accessToken = authResult.access_token 

    if (!accessToken) {
      throw new Error('No Google access token returned')
    }

    await axios.post('/api/accounts/auth/google/', { access_token: accessToken })
    router.push('/dashboard')
  } catch (e) {
    console.error('Google login failed', e)
  }
}
</script>

<style scoped>
.page {
  max-width: 400px;
  margin: 4rem auto;
  text-align: center;
}
button {
  padding: 0.75rem 1.5rem;
  border-radius: 999px;
  border: none;
  background: #4285f4;
  color: white;
  font-size: 1rem;
  cursor: pointer;
}
</style>
